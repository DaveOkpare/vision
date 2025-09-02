import { NextRequest, NextResponse } from "next/server"

export async function POST(req: NextRequest) {
  try {
    // Forward the form data directly to FastAPI backend
    const formData = await req.formData()
    
    // Check if FastAPI server is running
    const backendBaseUrl = process.env.BACKEND_URL || "http://localhost:8000"
    
    const response = await fetch(`${backendBaseUrl}/api/detect`, {
      method: "POST",
      body: formData,
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: "Unknown error" }))
      return NextResponse.json(
        { error: errorData.detail || errorData.error || "Backend error" }, 
        { status: response.status }
      )
    }
    
    const result = await response.json()
    
    // Transform the FastAPI response to match frontend expectations
    return NextResponse.json({
      ok: result.ok,
      imageUrl: `${backendBaseUrl}${result.imageUrl}`,
      targets: result.targets,
      results: result.results,
      message: result.message
    })
    
  } catch (err) {
    console.error("/api/detect proxy error:", err)
    
    // Check if it's a connection error (FastAPI not running)
    if (err instanceof TypeError && err.message.includes("fetch")) {
      return NextResponse.json({ 
        error: "FastAPI backend is not running. Start it with: uv run python api_server.py" 
      }, { status: 503 })
    }
    
    return NextResponse.json({ error: "Server error" }, { status: 500 })
  }
}

