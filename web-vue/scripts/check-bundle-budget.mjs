import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { gzipSync } from 'node:zlib'

const root = dirname(dirname(fileURLToPath(import.meta.url)))
const dist = join(root, 'dist')
const manifest = JSON.parse(readFileSync(join(dist, '.vite', 'manifest.json'), 'utf8'))
const budgetKb = Number(process.env.VITE_INITIAL_BUNDLE_BUDGET_KB || 150)

const entry = Object.values(manifest).find((item) => item.isEntry)
if (!entry) {
  throw new Error('No Vite entry chunk found in manifest')
}

const files = new Set()
function collect(chunk) {
  if (!chunk || !chunk.file) return
  if (chunk.file.endsWith('.js')) files.add(chunk.file)
  for (const key of chunk.imports || []) collect(manifest[key])
}
collect(entry)

let gzipBytes = 0
for (const file of files) {
  const raw = readFileSync(join(dist, file))
  gzipBytes += gzipSync(raw).byteLength
}

const gzipKb = gzipBytes / 1024
const label = `${gzipKb.toFixed(1)}KB gzip initial JS (${files.size} chunks)`
console.log(`Bundle budget: ${label}; target <= ${budgetKb}KB`)

if (gzipKb > budgetKb) {
  throw new Error(`Initial JS bundle over budget: ${label}`)
}
