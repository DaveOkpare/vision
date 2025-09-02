"use client"

import React from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button, buttonVariants } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { ImageUpload } from "@/components/image-upload"
import { Github } from "lucide-react"

type ApiResult = {
  ok: boolean
  imageUrl: string
  targets: string[]
  results: { object: string; confidence: string; confidence_score: number; bbox: number[] }[]
  message?: string
  error?: string
}

export default function Home() {
  const [file, setFile] = React.useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = React.useState<string | null>(null)
  const [targets, setTargets] = React.useState("")
  const [isLoading, setIsLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const [data, setData] = React.useState<ApiResult | null>(null)

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setData(null)
    if (!file) {
      setError("Please select an image file.")
      return
    }
    const form = new FormData()
    form.append("file", file)
    form.append("targets", targets)
    setIsLoading(true)
    try {
      const res = await fetch("/api/detect", { method: "POST", body: form })
      const json = (await res.json()) as ApiResult
      if (!res.ok) {
        throw new Error(json?.error || "Request failed")
      }
      setData(json)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen w-full px-6 py-10 md:px-10">
      <div className="mx-auto w-full max-w-5xl grid gap-6">
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between gap-4">
              <div>
                <CardTitle>Image Object Detection</CardTitle>
                <CardDescription>Upload an image and specify items to detect (comma-separated).</CardDescription>
              </div>
              <a
                href={process.env.NEXT_PUBLIC_GITHUB_URL ?? "https://github.com"}
                target="_blank"
                rel="noopener noreferrer"
                aria-label="View project on GitHub"
                className={buttonVariants({ variant: "outline", size: "sm" })}
              >
                <Github className="mr-2 h-4 w-4" />
                GitHub
              </a>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={onSubmit} className="grid gap-5">
              <div className="grid gap-2">
                <Label htmlFor="file">Image</Label>
                <ImageUpload
                  onFileSelected={(f) => { setFile(f); setData(null); setError(null) }}
                  previewUrl={previewUrl}
                  setPreviewUrl={setPreviewUrl}
                  isLoading={isLoading}
                  resultUrl={data?.imageUrl ?? null}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="targets">What to detect</Label>
                <Textarea
                  id="targets"
                  placeholder="e.g. red car, person, traffic light"
                  value={targets}
                  onChange={(e) => setTargets(e.target.value)}
                />
              </div>
              <div className="flex items-center gap-3">
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? "Detecting…" : "Run Detection"}
                </Button>
              </div>
              {error && (
                <div className="text-sm text-red-600 dark:text-red-400" role="alert">
                  {error}
                </div>
              )}
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
