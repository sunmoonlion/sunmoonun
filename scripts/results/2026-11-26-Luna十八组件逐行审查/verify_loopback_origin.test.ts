import { expect, it } from 'vitest'
import { parseServerEnv } from '@/env/server-schema'

it('accepts the IPv4 loopback but rejects the configured IPv6 loopback', () => {
  const config = { DEPLOYMENT_ENV: 'test', NODE_ENV: 'development' }
  expect(parseServerEnv({ ...config, APP_ORIGIN: 'http://127.0.0.1:3010' }).DEPLOYMENT_ENV).toBe('test')
  expect(new URL('http://[::1]:3010').hostname).toBe('[::1]')
  expect(() => parseServerEnv({ ...config, APP_ORIGIN: 'http://[::1]:3010' })).toThrow(/loopback/)
})
