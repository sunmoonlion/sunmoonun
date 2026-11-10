"""Reconcile public email signup through Casdoor's administrative API.

Called only by the application which owns public registration. No SMTP password,
API response, or user data is included in errors or acceptance output.
"""
from datetime import datetime, timezone
import re


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def matches(actual, expected):
    """Compare managed fields; Casdoor adds default fields to nested objects."""
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(matches(actual.get(k), v) for k, v in expected.items())
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(
            matches(a, e) for a, e in zip(actual, expected)
        )
    return type(actual) is type(expected) and actual == expected


def validate_settings(settings, password):
    require(type(settings.get('enabled')) is bool, 'Signup enabled must be boolean')
    if not settings['enabled']:
        return
    require(settings.get('smtp_host') == 'smtpdm.aliyun.com' and settings.get('smtp_port') == 465,
            'Signup requires the configured Aliyun Hangzhou TLS SMTP endpoint')
    require(isinstance(settings.get('smtp_username'), str) and re.fullmatch(
        r'[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', settings['smtp_username']),
        'Signup SMTP username must be a sender email address')
    require(isinstance(password, str) and 10 <= len(password) <= 128 and not any(c.isspace() for c in password),
            'Signup SMTP password is missing or malformed')


def disable_builtin_signup(api):
    identity = 'admin/app-built-in'
    application = api('GET', '/api/get-application', params={'id': identity})
    require(application and application.get('organization') == 'built-in',
            'Built-in application boundary differs')
    if application.get('enableSignUp') is not False:
        api('POST', '/api/update-application', dict(application, enableSignUp=False),
            params={'id': identity, 'columns': 'enable_sign_up'})
    current = api('GET', '/api/get-application', params={'id': identity})
    require(current and current.get('enableSignUp') is False, 'Built-in signup remains enabled')


def configure_signup(api, application, settings, password):
    """Enable only after the provider and required email-verification policy exist.

    The caller has already checked the client's secret, redirect URIs, grants and
    organization. Rollback disables signup and detaches the SMTP provider, since
    disabling signup alone does not disable Casdoor's send-code endpoint.
    """
    validate_settings(settings, password)
    require(application.get('organization') == 'sunmoonai' and application.get('owner') == 'admin',
            'Public signup must belong to the ordinary-user organization')
    name = application['name']
    identity = 'admin/' + name
    provider_name = name + '-signup-email'
    provider_id = 'admin/' + provider_name
    require(all(item.get('name') == provider_name for item in (application.get('providers') or [])),
            'Existing signup providers differ; explicit migration required')
    disable_builtin_signup(api)
    if settings['enabled']:
        provider = {
            'owner': 'admin', 'name': provider_name, 'displayName': 'SunMoonAI registration email',
            'category': 'Email', 'type': 'Default', 'host': settings['smtp_host'],
            'port': settings['smtp_port'], 'sslMode': 'Enable', 'disableSsl': False,
            'enableProxy': False, 'clientId': settings['smtp_username'],
            'clientId2': settings['smtp_username'], 'clientSecret2': 'SunMoonAI',
            'title': 'SunMoonAI 注册验证码',
            'content': '<p>您的 SunMoonAI 注册验证码为：<strong>%s</strong>。</p>'
                       '<p>请尽快填写。若非本人操作，请忽略此邮件。请勿向他人透露验证码。</p>',
        }
        current = api('GET', '/api/get-provider', params={'id': provider_id})
        require(current is None or (current.get('owner') == 'admin' and current.get('category') == 'Email'
                                    and current.get('type') == 'Default'),
                'Signup provider name is already used by another provider type')
        # The API masks passwords. Always reconcile the explicitly supplied secret,
        # never interpret "***" as proof that the configured credential matches.
        value = dict(current or {}, **provider, clientSecret=password)
        if current is None:
            api('POST', '/api/add-provider', dict(value, createdTime=datetime.now(timezone.utc).isoformat()))
        else:
            api('POST', '/api/update-provider', value, params={'id': provider_id})
        require(matches(api('GET', '/api/get-provider', params={'id': provider_id}), provider),
                'Signup SMTP provider was not applied')

        items = [
            {'name': 'Email', 'visible': True, 'required': True, 'prompted': False, 'rule': 'Normal'},
            {'name': 'Username', 'visible': True, 'required': True, 'prompted': False, 'rule': 'Normal'},
            {'name': 'Password', 'visible': True, 'required': True, 'prompted': False, 'rule': 'Normal'},
            {'name': 'Confirm password', 'visible': True, 'required': True, 'prompted': False, 'rule': 'Normal'},
            {'name': 'Signup button', 'visible': True, 'required': False, 'prompted': False, 'rule': 'Normal'},
        ]
        desired = {
            'enableSignUp': True, 'enableCodeSignin': False, 'enableGuestSignin': False,
            'signupItems': items, 'providers': [{'name': provider_name, 'rule': 'signup'}],
            'codeResendTimeout': 60, 'signupUrl': '', 'signupHtml': '',
        }
        # Casdoor fills the default signin items on read. Preserve their other
        # properties, but make the registration link available in the login flow.
        signin_items = application.get('signinItems') or []
        if signin_items:
            desired['signinItems'] = [dict(item, visible=True) if item.get('name') == 'Signup link'
                                      else item for item in signin_items]
            if not any(item.get('name') == 'Signup link' for item in signin_items):
                desired['signinItems'].append({'name': 'Signup link', 'visible': True})
    else:
        desired = {'enableSignUp': False, 'providers': [], 'signupItems': []}
    if not matches(application, desired):
        api('POST', '/api/update-application', dict(application, **desired), params={'id': identity})
    current = api('GET', '/api/get-application', params={'id': identity})
    require(matches(current, desired), 'Public signup policy was not applied')
    return {
        'enabled': settings['enabled'], 'email_verification_required': settings['enabled'],
        'invitation_required': False, 'builtin_signup_disabled': True,
        'smtp_delivery_verified': False,
    }
