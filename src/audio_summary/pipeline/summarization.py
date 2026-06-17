"""Text summarization with Qwen3 on Apple Silicon via mlx-lm."""

from mlx_lm import generate, load

SYSTEM_PROMPT = "I would like for you to assume the role of a Technical Expert."

USER_PROMPT_TEMPLATE = """Generate a concise summary of the text below.
Text : {text}
Add a title to the summary.
Make sure your summary has useful and true information about the main points of the topic.
Begin with a short introduction explaining the topic. If you can, use bullet points to list important details,
and finish your summary with a concluding sentence."""


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
