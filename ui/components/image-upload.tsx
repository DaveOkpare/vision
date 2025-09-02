"use client"

import React from "react"
import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"

type Props = {
  onFileSelected: (file: File | null) => void
  previewUrl?: string | null
  setPreviewUrl: (url: string | null) => void
}

export function ImageUpload({ onFileSelected, previewUrl, setPreviewUrl }: Props) {
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

  return (
    <Card className={cn("border-dashed", isDragging && "border-ring bg-accent/30")}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={onDrop}
    >
      <CardContent className="p-4">
        <div className="flex flex-col items-center justify-center gap-3 text-center">
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
          <input
            ref={inputRef}
            type="file"
            accept="image/png,image/jpeg,image/webp"
            multiple={false}
            onChange={onChange}
            className="hidden"
          />

          {previewUrl && (
            <div className="mt-3 w-full">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={previewUrl}
                alt="Preview"
                className="mx-auto max-h-[60vh] max-w-full rounded-md border object-contain"
              />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
