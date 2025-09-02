"use client"

import React from "react"
import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { Skeleton } from "@/components/ui/skeleton"
import { buttonVariants } from "@/components/ui/button"

type Props = {
  onFileSelected: (file: File | null) => void
  previewUrl?: string | null
  setPreviewUrl: (url: string | null) => void
  isLoading?: boolean
  resultUrl?: string | null
}

export function ImageUpload({ onFileSelected, previewUrl, setPreviewUrl, isLoading = false, resultUrl }: Props) {
  const inputRef = React.useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = React.useState(false)

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return
    const file = files[0]
    if (!file.type.startsWith("image/")) return
    onFileSelected(file)
    const url = URL.createObjectURL(file)
    setPreviewUrl(url)
  }

  const onDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
    handleFiles(e.dataTransfer.files)
  }

  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files)
  }

  const currentUrl = (resultUrl || previewUrl) as string | undefined

  const filenameFromUrl = (url: string) => {
    try {
      const u = new URL(url, window.location.origin)
      const parts = u.pathname.split("/")
      return parts[parts.length - 1] || "image"
    } catch {
      const parts = url.split("/")
      return parts[parts.length - 1] || "image"
    }
  }

  const handleDownload = async (url?: string) => {
    if (!url) return
    try {
      const res = await fetch(url)
      const blob = await res.blob()
      const blobUrl = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = blobUrl
      const name = filenameFromUrl(url)
      a.download = name
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(blobUrl)
    } catch (e) {
      // Fallback: navigate to the URL
      window.open(url, "_blank")
    }
  }


  return (
    <>
    <Card className={cn("border-dashed", isDragging && "border-ring bg-accent/30")}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={onDrop}
    >
      <CardContent className="p-4">
        <div className="flex flex-col items-center justify-center gap-3 text-center">
          {!isLoading && !resultUrl && !previewUrl && (
            <>
              <div className="text-sm text-muted-foreground">
                Drag and drop an image here, or
              </div>
              <button
                type="button"
                className="underline underline-offset-4 text-sm"
                onClick={() => inputRef.current?.click()}
              >
                browse files
              </button>
              <div className="text-xs text-muted-foreground">Only one image at a time</div>
            </>
          )}

          <input
            ref={inputRef}
            type="file"
            accept="image/png,image/jpeg,image/webp"
            multiple={false}
            onChange={onChange}
            className="hidden"
          />

          {isLoading && (
            <div className="mt-2 w-full">
              <Skeleton className="h-[48vh] w-full max-h-[600px]" />
            </div>
          )}

          {!isLoading && (resultUrl || previewUrl) && (
            <div className="mt-2 w-full">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={resultUrl || (previewUrl as string)}
                alt="Preview"
                className="mx-auto max-h-[60vh] max-w-full rounded-md border object-contain"
              />
              <div className="mt-3 flex items-center justify-center gap-3">
                <button
                  type="button"
                  onClick={() => handleDownload(currentUrl)}
                  className={buttonVariants({ variant: "default", size: "default" })}
                >
                  Download image
                </button>
                {!isLoading && (
                  <button
                    type="button"
                    onClick={() => inputRef.current?.click()}
                    className={cn(buttonVariants({ variant: "outline", size: "default" }))}
                  >
                    Change image
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
    </>
  )
}
