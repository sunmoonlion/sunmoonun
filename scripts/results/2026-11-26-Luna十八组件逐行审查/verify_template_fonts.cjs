// 从六仓根目录运行。模板 CSS 经项目安装的 PostCSS 和 Tailwind 处理后送入本机 Chromium。
const { createRequire } = require('node:module')
const { readFileSync } = require('node:fs')
const { resolve } = require('node:path')
const compilerRoot = resolve('knowfeed-app/knowfeed-admin-frontend/app')
const load = createRequire(compilerRoot + '/package.json')
const postcss = createRequire(load.resolve('@tailwindcss/postcss'))('postcss')
const tailwind = load('@tailwindcss/postcss')
const { chromium } = load('@playwright/test')
const assert = require('node:assert/strict')

async function main() {
  const browser = await chromium.launch()
  try {
    for (const surface of ['admin', 'web']) {
      const path = resolve('tpl-app/tpl-' + surface + '-frontend/app/app/globals.css')
      const input = readFileSync(path, 'utf8')
      const compiled = await postcss([tailwind({ base: compilerRoot })]).process(input, {
        from: compilerRoot + '/app/audit-' + surface + '.css',
      })
      const page = await browser.newPage()
      await page.setContent('<p>报表</p>')
      const baseline = await page.locator('html').evaluate(el => getComputedStyle(el).fontFamily)
      await page.addStyleTag({ content: compiled.css })
      const actual = await page.locator('html').evaluate(el => getComputedStyle(el).fontFamily)
      console.log(surface, baseline, actual)
      if (surface === 'admin') assert.equal(actual, baseline)
      else assert.match(actual, /sans-serif/)
      await page.close()
    }
  } finally {
    await browser.close()
  }
}
main().catch(error => { console.error(error); process.exitCode = 1 })
