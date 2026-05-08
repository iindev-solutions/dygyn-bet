import type { Participant } from '@/api/types'
import { apiUrl } from '@/api/client'
import { initials } from './display'

export interface StoryCardResult {
  shared: boolean
  message: string
}

export async function createAndShareStoryCard(picks: Participant[]): Promise<StoryCardResult> {
  const images = await Promise.all(
    picks.map((participant) => loadCanvasImage(apiUrl(`/participants/${participant.id}/avatar`))),
  )
  const canvas = document.createElement('canvas')
  canvas.width = 1080
  canvas.height = 1920
  const ctx = canvas.getContext('2d')
  if (!ctx) throw new Error('Canvas недоступен')

  const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height)
  gradient.addColorStop(0, '#f2b84b')
  gradient.addColorStop(0.28, '#1f2430')
  gradient.addColorStop(1, '#0f1115')
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  ctx.fillStyle = 'rgba(255,255,255,.12)'
  ctx.beginPath()
  ctx.arc(920, 230, 270, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.arc(120, 1660, 340, 0, Math.PI * 2)
  ctx.fill()

  ctx.fillStyle = '#10131a'
  ctx.font = '900 34px Arial'
  ctx.fillText('ГОЛОС БОЛЕЛЬЩИКА', 90, 116)
  ctx.fillStyle = '#ffffff'
  ctx.font = '900 76px Arial'
  wrapCanvasText(ctx, 'В этом году я голосую за', 90, 220, 900, 84)

  if (picks.length === 1) {
    drawStoryPick(ctx, picks[0], images[0], 90, 420, 900, 920)
  } else {
    drawStoryPick(ctx, picks[0], images[0], 90, 395, 900, 570)
    drawStoryPick(ctx, picks[1], images[1], 90, 1015, 900, 570)
  }

  ctx.fillStyle = '#f8f1e4'
  ctx.font = '800 48px Arial'
  wrapCanvasText(ctx, 'Заходи и голосуй за своего фаворита', 90, 1665, 900, 58)
  ctx.fillStyle = '#f2b84b'
  ctx.font = '900 54px Arial'
  wrapCanvasText(ctx, '@dygyn_games_bet_bot', 90, 1770, 900, 62)

  return shareOrDownloadStoryCard(canvas)
}

function loadCanvasImage(src: string): Promise<HTMLImageElement | null> {
  return new Promise((resolve) => {
    const img = new Image()
    img.decoding = 'async'
    img.onload = () => resolve(img)
    img.onerror = () => resolve(null)
    img.src = src
  })
}

async function shareOrDownloadStoryCard(canvas: HTMLCanvasElement): Promise<StoryCardResult> {
  const blob = await canvasToBlob(canvas)
  const file = new File([blob], 'dygyn-story-card.png', { type: 'image/png' })
  if (navigator.canShare?.({ files: [file] }) && navigator.share) {
    try {
      await navigator.share({ files: [file], title: 'Игры Дыгына', text: 'Моя сторис-карточка' })
      return {
        shared: true,
        message:
          'Если Instagram не выбран: сохраните PNG и откройте Instagram → Stories → Галерея.',
      }
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') {
        return {
          shared: false,
          message:
            'Отмена. Можно нажать «Сторис PNG» ещё раз и выбрать Instagram или сохранить файл.',
        }
      }
    }
  }

  downloadBlob(blob, 'dygyn-story-card.png')
  return {
    shared: false,
    message: 'PNG скачан. Дальше: Instagram → Stories → Галерея/Загрузки → выбрать карточку.',
  }
}

function canvasToBlob(canvas: HTMLCanvasElement): Promise<Blob> {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) resolve(blob)
      else reject(new Error('Не удалось создать PNG'))
    }, 'image/png')
  })
}

function downloadBlob(blob: Blob, filename: string) {
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.download = filename
  link.href = url
  link.click()
  window.setTimeout(() => URL.revokeObjectURL(url), 1000)
}

function drawStoryPick(
  ctx: CanvasRenderingContext2D,
  participant: Participant | undefined,
  image: HTMLImageElement | null | undefined,
  x: number,
  y: number,
  width: number,
  height: number,
) {
  if (!participant) return
  ctx.save()
  roundedCanvasPath(ctx, x, y, width, height, 44)
  ctx.fillStyle = 'rgba(15,17,21,.88)'
  ctx.fill()
  ctx.strokeStyle = 'rgba(242,184,75,.55)'
  ctx.lineWidth = 3
  ctx.stroke()
  ctx.restore()

  const photoHeight = Math.round(height * 0.68)
  if (image) drawCoverImage(ctx, image, x + 22, y + 22, width - 44, photoHeight, 34)
  else drawStoryFallback(ctx, participant, x + 22, y + 22, width - 44, photoHeight, 34)

  ctx.fillStyle = 'rgba(242,184,75,.92)'
  roundedCanvasPath(ctx, x + 44, y + photoHeight - 52, 190, 74, 28)
  ctx.fill()
  ctx.fillStyle = '#1b1204'
  ctx.font = '900 34px Arial'
  ctx.fillText(`${participant.confidence_points || 0} очков`, x + 70, y + photoHeight - 5)

  ctx.fillStyle = '#ffffff'
  ctx.font = '900 56px Arial'
  wrapCanvasText(ctx, participant.name, x + 42, y + photoHeight + 108, width - 84, 62)
  ctx.fillStyle = '#f2b84b'
  ctx.font = '800 34px Arial'
  wrapCanvasText(
    ctx,
    participant.region || 'улус не указан',
    x + 42,
    y + height - 44,
    width - 84,
    40,
  )
}

function drawCoverImage(
  ctx: CanvasRenderingContext2D,
  image: HTMLImageElement,
  x: number,
  y: number,
  width: number,
  height: number,
  radius: number,
) {
  const scale = Math.max(width / image.width, height / image.height)
  const sourceWidth = width / scale
  const sourceHeight = height / scale
  const sourceX = (image.width - sourceWidth) / 2
  const sourceY = Math.max(0, (image.height - sourceHeight) * 0.18)
  ctx.save()
  roundedCanvasPath(ctx, x, y, width, height, radius)
  ctx.clip()
  ctx.drawImage(image, sourceX, sourceY, sourceWidth, sourceHeight, x, y, width, height)
  ctx.restore()
}

function drawStoryFallback(
  ctx: CanvasRenderingContext2D,
  participant: Participant,
  x: number,
  y: number,
  width: number,
  height: number,
  radius: number,
) {
  ctx.save()
  roundedCanvasPath(ctx, x, y, width, height, radius)
  ctx.fillStyle = 'rgba(242,184,75,.16)'
  ctx.fill()
  ctx.fillStyle = '#f2b84b'
  ctx.font = '900 112px Arial'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(initials(participant.name), x + width / 2, y + height / 2)
  ctx.textAlign = 'left'
  ctx.textBaseline = 'alphabetic'
  ctx.restore()
}

function roundedCanvasPath(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  width: number,
  height: number,
  radius: number,
) {
  const r = Math.min(radius, width / 2, height / 2)
  ctx.beginPath()
  ctx.moveTo(x + r, y)
  ctx.lineTo(x + width - r, y)
  ctx.quadraticCurveTo(x + width, y, x + width, y + r)
  ctx.lineTo(x + width, y + height - r)
  ctx.quadraticCurveTo(x + width, y + height, x + width - r, y + height)
  ctx.lineTo(x + r, y + height)
  ctx.quadraticCurveTo(x, y + height, x, y + height - r)
  ctx.lineTo(x, y + r)
  ctx.quadraticCurveTo(x, y, x + r, y)
  ctx.closePath()
}

function wrapCanvasText(
  ctx: CanvasRenderingContext2D,
  text: string,
  x: number,
  y: number,
  maxWidth: number,
  lineHeight: number,
) {
  const words = String(text).split(' ')
  let line = ''
  let currentY = y
  for (const word of words) {
    const testLine = line ? `${line} ${word}` : word
    if (ctx.measureText(testLine).width > maxWidth && line) {
      ctx.fillText(line, x, currentY)
      line = word
      currentY += lineHeight
    } else {
      line = testLine
    }
  }
  if (line) ctx.fillText(line, x, currentY)
}
