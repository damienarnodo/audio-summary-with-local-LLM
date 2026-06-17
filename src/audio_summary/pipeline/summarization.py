"""Text summarization with Qwen3 on Apple Silicon via mlx-lm."""

from mlx_lm import generate, load

SYSTEM_PROMPT = (
    "You are an expert technical analyst who writes clear, faithful summaries of "
    "transcribed audio. Rules you always follow:\n"
    "- Write the summary in the SAME language as the transcript.\n"
    "- Only use information present in the transcript; never invent facts, names, "
    "or numbers. If something is unclear or cut off, say so rather than guessing.\n"
    "- Preserve technical terms, product names, and acronyms exactly as spoken.\n"
    "- The text is raw speech-to-text: ignore filler, repetitions, and transcription "
    "noise, and focus on the substance."
)

USER_PROMPT_TEMPLATE = """Summarize the transcript below as a Markdown document with this exact structure:

# <a short, descriptive title capturing the main topic>

**TL;DR:** <2-3 sentence overview a busy reader could read alone>

## Key points
- <the most important ideas, one per bullet — aim for 5-8 bullets>

## Details that matter
- <specific facts, examples, definitions, numbers, or steps worth keeping>

## Takeaways
- <conclusions, recommendations, or open questions raised in the discussion>

Keep it concise and skimmable. Omit any section that the transcript genuinely does not support.

Transcript:
{text}"""


def summarize_text(text: str, model_repo: str, max_tokens: int = 2048) -> str:
    """Summarize ``text`` using the Qwen3 model at ``model_repo``."""
    print(f"Loading summarization model: {model_repo}")
    model, tokenizer = load(model_repo)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT_TEMPLATE.format(text=text)},
    ]

    # Qwen3 supports a "thinking" mode; disable it for clean, direct summaries.
    prompt = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        enable_thinking=False,
    )

    summary = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=max_tokens,
        verbose=False,
    )
    return summary.strip()
