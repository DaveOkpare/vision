"use client"

import React from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button, buttonVariants } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { ImageUpload } from "@/components/image-upload"

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
    } catch (err: any) {
      setError(err?.message || "Something went wrong")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen w-full px-6 py-10 md:px-10">
      <div className="mx-auto w-full max-w-5xl grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Image Object Detection</CardTitle>
            <CardDescription>Upload an image and specify items to detect (comma-separated).</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={onSubmit} className="grid gap-5">
              <div className="grid gap-2">
                <Label htmlFor="file">Image</Label>
                <ImageUpload onFileSelected={setFile} previewUrl={previewUrl} setPreviewUrl={setPreviewUrl} />
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

        <Card>
          <CardHeader>
            <CardTitle>Results</CardTitle>
            <CardDescription>Detection output and uploaded image.</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading && (
              <div className="grid gap-4">
                <Skeleton className="h-6 w-40" />
                <Skeleton className="h-64 w-full" />
                <Skeleton className="h-24 w-full" />
              </div>
            )}
            {!isLoading && !data && (
              <div className="text-sm text-muted-foreground">No results yet. Submit an image to start.</div>
            )}
            {!isLoading && data && (
              <div className="grid gap-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-start">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={data.imageUrl}
                    alt="Uploaded"
                    className="rounded-md border w-full h-auto object-contain md:col-span-2"
                  />
                  <div className="text-sm">
                    <div className="mb-2 font-medium">Targets</div>
                    <ul className="list-disc pl-5 space-y-1">
                      {data.targets.length > 0 ? (
                        data.targets.map((t) => <li key={t}>{t}</li>)
                      ) : (
                        <li className="text-muted-foreground">None provided</li>
                      )}
                    </ul>
                    <div className="mt-4">
                      <a
                        href={data.imageUrl}
                        download
                        className={buttonVariants({ variant: "default", size: "default" })}
                      >
                        Download image
                      </a>
                    </div>
                  </div>
                </div>
                <div className="grid gap-2">
                  <div className="font-medium">Detections</div>
                  <div className="rounded-md border divide-y">
                    <div className="grid grid-cols-4 gap-2 p-2 text-xs text-muted-foreground">
                      <div>Object</div>
                      <div>Confidence</div>
                      <div>Score</div>
                      <div>BBox</div>
                    </div>
                    {data.results.length === 0 && (
                      <div className="p-2 text-sm text-muted-foreground">No detections</div>
                    )}
                    {data.results.map((r, idx) => (
                      <div key={idx} className="grid grid-cols-4 gap-2 p-2 text-sm">
                        <div>{r.object}</div>
                        <div className="capitalize">{r.confidence}</div>
                        <div>{r.confidence_score.toFixed(1)}%</div>
                        <div>[{r.bbox.join(", ")}]</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
