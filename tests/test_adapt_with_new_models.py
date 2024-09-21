import asyncio
import os
import pytest
import time
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.models.github_model_backend import (
    GitHubModelBackend,
    GitHubModelError,
    GitHubAPIError,
)
from camel.models.gemini_model_backend import (
    GeminiModelBackend,
    GeminiModelError,
    GeminiAPIError,
)

# Ensure these environment variables are set before running the tests
GITHUB_API_KEY = os.environ.get("GITHUB_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


@pytest.fixture
def github_model():
    return ModelFactory.create(
        model_platform=ModelPlatformType.GITHUB,
        model_type=ModelType.GITHUB_COPILOT,
        model_config_dict={},
        api_key=GITHUB_API_KEY,
    )


@pytest.fixture
def gemini_model():
    return ModelFactory.create(
        model_platform=ModelPlatformType.GEMINI,
        model_type=ModelType.GEMINI_1_5_PRO,
        model_config_dict={},
        api_key=GEMINI_API_KEY,
    )


def test_model_factory():
    github_model = ModelFactory.create(
        model_platform=ModelPlatformType.GITHUB,
        model_type=ModelType.GITHUB_COPILOT,
        model_config_dict={},
        api_key=GITHUB_API_KEY,
    )
    assert isinstance(github_model, GitHubModelBackend)

    gemini_model = ModelFactory.create(
        model_platform=ModelPlatformType.GEMINI,
        model_type=ModelType.GEMINI_1_5_PRO,
        model_config_dict={},
        api_key=GEMINI_API_KEY,
    )
    assert isinstance(gemini_model, GeminiModelBackend)


@pytest.mark.asyncio
async def test_text_generation(github_model, gemini_model):
    prompt = "Explain the concept of machine learning in simple terms."

    start_time = time.time()
    github_response = await github_model.generate(
        prompt, max_tokens=100, temperature=0.7
    )
    github_time = time.time() - start_time
    assert isinstance(github_response, str)
    assert len(github_response) > 0

    start_time = time.time()
    gemini_response = await gemini_model.generate(
        prompt, max_tokens=100, temperature=0.7
    )
    gemini_time = time.time() - start_time
    assert isinstance(gemini_response, str)
    assert len(gemini_response) > 0

    print(f"GitHub generation time: {github_time:.2f}s")
    print(f"Gemini generation time: {gemini_time:.2f}s")


@pytest.mark.asyncio
async def test_token_counting(github_model, gemini_model):
    text = "This is a sample text for token counting."

    start_time = time.time()
    github_tokens = await github_model.get_token_count(text)
    github_time = time.time() - start_time
    assert isinstance(github_tokens, int)
    assert github_tokens > 0

    start_time = time.time()
    gemini_tokens = await gemini_model.get_token_count(text)
    gemini_time = time.time() - start_time
    assert isinstance(gemini_tokens, int)
    assert gemini_tokens > 0

    print(f"GitHub token counting time: {github_time:.2f}s")
    print(f"Gemini token counting time: {gemini_time:.2f}s")

    # Test caching
    start_time = time.time()
    cached_github_tokens = await github_model.get_token_count(text)
    cached_github_time = time.time() - start_time
    assert cached_github_tokens == github_tokens

    start_time = time.time()
    cached_gemini_tokens = await gemini_model.get_token_count(text)
    cached_gemini_time = time.time() - start_time
    assert cached_gemini_tokens == gemini_tokens

    print(f"GitHub cached token counting time: {cached_github_time:.2f}s")
    print(f"Gemini cached token counting time: {cached_gemini_time:.2f}s")


@pytest.mark.asyncio
async def test_embeddings(github_model, gemini_model):
    text = "This is a sample text for generating embeddings."

    try:
        start_time = time.time()
        github_embeddings = await github_model.embeddings(text)
        github_time = time.time() - start_time
        assert isinstance(github_embeddings, list)
        assert len(github_embeddings) > 0
        assert all(isinstance(x, float) for x in github_embeddings)
        print(f"GitHub embeddings time: {github_time:.2f}s")

        # Test caching
        start_time = time.time()
        cached_github_embeddings = await github_model.embeddings(text)
        cached_github_time = time.time() - start_time
        assert cached_github_embeddings == github_embeddings
        print(f"GitHub cached embeddings time: {cached_github_time:.2f}s")
    except NotImplementedError:
        pytest.skip("GitHub model does not support embeddings")

    try:
        start_time = time.time()
        gemini_embeddings = await gemini_model.embeddings(text)
        gemini_time = time.time() - start_time
        assert isinstance(gemini_embeddings, list)
        assert len(gemini_embeddings) > 0
        assert all(isinstance(x, float) for x in gemini_embeddings)
        print(f"Gemini embeddings time: {gemini_time:.2f}s")

        # Test caching
        start_time = time.time()
        cached_gemini_embeddings = await gemini_model.embeddings(text)
        cached_gemini_time = time.time() - start_time
        assert cached_gemini_embeddings == gemini_embeddings
        print(f"Gemini cached embeddings time: {cached_gemini_time:.2f}s")
    except NotImplementedError:
        pytest.skip("Gemini model does not support embeddings")


@pytest.mark.asyncio
async def test_model_info(github_model, gemini_model):
    start_time = time.time()
    github_info = await github_model.get_model_info()
    github_time = time.time() - start_time
    assert isinstance(github_info, dict)
    assert "model_name" in github_info
    assert "model_type" in github_info

    start_time = time.time()
    gemini_info = await gemini_model.get_model_info()
    gemini_time = time.time() - start_time
    assert isinstance(gemini_info, dict)
    assert "model_name" in gemini_info
    assert "model_type" in gemini_info

    print(f"GitHub model info time: {github_time:.2f}s")
    print(f"Gemini model info time: {gemini_time:.2f}s")


@pytest.mark.asyncio
async def test_error_handling(github_model, gemini_model):
    with pytest.raises(GitHubModelError):
        await github_model.generate("", max_tokens=-1, temperature=2.0)

    with pytest.raises(GeminiModelError):
        await gemini_model.generate("", max_tokens=-1, temperature=2.0)


@pytest.mark.asyncio
async def test_api_error_handling(github_model, gemini_model):
    # Simulate API errors by temporarily changing the API key
    github_model.set_api_key("invalid_key")
    gemini_model.set_api_key("invalid_key")

    with pytest.raises(GitHubAPIError):
        await github_model.generate("Test prompt", max_tokens=10, temperature=0.7)

    with pytest.raises(GeminiAPIError):
        await gemini_model.generate("Test prompt", max_tokens=10, temperature=0.7)


@pytest.mark.asyncio
async def test_concurrent_requests(github_model, gemini_model):
    prompts = ["Test prompt 1", "Test prompt 2", "Test prompt 3"]

    async def generate_concurrent(model, prompt):
        return await model.generate(prompt, max_tokens=50, temperature=0.7)

    start_time = time.time()
    github_tasks = [generate_concurrent(github_model, prompt) for prompt in prompts]
    github_results = await asyncio.gather(*github_tasks)
    github_time = time.time() - start_time

    assert len(github_results) == len(prompts)
    assert all(isinstance(result, str) for result in github_results)

    start_time = time.time()
    gemini_tasks = [generate_concurrent(gemini_model, prompt) for prompt in prompts]
    gemini_results = await asyncio.gather(*gemini_tasks)
    gemini_time = time.time() - start_time

    assert len(gemini_results) == len(prompts)
    assert all(isinstance(result, str) for result in gemini_results)

    print(f"GitHub concurrent requests time: {github_time:.2f}s")
    print(f"Gemini concurrent requests time: {gemini_time:.2f}s")


@pytest.mark.asyncio
async def test_long_input_handling(github_model, gemini_model):
    long_prompt = "Test " * 1000  # Create a long input

    start_time = time.time()
    github_response = await github_model.generate(
        long_prompt, max_tokens=50, temperature=0.7
    )
    github_time = time.time() - start_time
    assert isinstance(github_response, str)
    assert len(github_response) > 0

    start_time = time.time()
    gemini_response = await gemini_model.generate(
        long_prompt, max_tokens=50, temperature=0.7
    )
    gemini_time = time.time() - start_time
    assert isinstance(gemini_response, str)
    assert len(gemini_response) > 0

    print(f"GitHub long input handling time: {github_time:.2f}s")
    print(f"Gemini long input handling time: {gemini_time:.2f}s")


@pytest.mark.asyncio
async def test_set_api_key(github_model, gemini_model):
    new_api_key = "new_test_api_key"

    github_model.set_api_key(new_api_key)
    assert github_model.api_key == new_api_key

    gemini_model.set_api_key(new_api_key)
    assert gemini_model.api_key == new_api_key


@pytest.mark.asyncio
async def test_check_availability(github_model, gemini_model):
    start_time = time.time()
    github_available = await github_model.check_availability()
    github_time = time.time() - start_time
    assert isinstance(github_available, bool)

    start_time = time.time()
    gemini_available = await gemini_model.check_availability()
    gemini_time = time.time() - start_time
    assert isinstance(gemini_available, bool)

    print(f"GitHub availability check time: {github_time:.2f}s")
    print(f"Gemini availability check time: {gemini_time:.2f}s")


@pytest.mark.asyncio
async def test_image_generation(github_model, gemini_model):
    prompt = "A beautiful sunset over a calm ocean"

    start_time = time.time()
    github_image_url = await github_model.generate_image(prompt)
    github_time = time.time() - start_time
    assert isinstance(github_image_url, str)
    assert github_image_url.startswith("http")

    start_time = time.time()
    gemini_image_url = await gemini_model.generate_image(prompt)
    gemini_time = time.time() - start_time
    assert isinstance(gemini_image_url, str)
    assert gemini_image_url.startswith("http")

    print(f"GitHub image generation time: {github_time:.2f}s")
    print(f"Gemini image generation time: {gemini_time:.2f}s")


@pytest.mark.asyncio
async def test_image_analysis(github_model, gemini_model):
    image_path = "path/to/test/image.jpg"  # Replace with an actual test image path

    start_time = time.time()
    github_analysis = await github_model.analyze_image(image_path)
    github_time = time.time() - start_time
    assert isinstance(github_analysis, dict)
    assert "analysis" in github_analysis

    start_time = time.time()
    gemini_analysis = await gemini_model.analyze_image(image_path)
    gemini_time = time.time() - start_time
    assert isinstance(gemini_analysis, dict)
    assert "analysis" in gemini_analysis

    print(f"GitHub image analysis time: {github_time:.2f}s")
    print(f"Gemini image analysis time: {gemini_time:.2f}s")


@pytest.mark.asyncio
async def test_speech_to_text(github_model, gemini_model):
    audio_path = "path/to/test/audio.wav"  # Replace with an actual test audio path

    start_time = time.time()
    github_transcription = await github_model.speech_to_text(audio_path)
    github_time = time.time() - start_time
    assert isinstance(github_transcription, str)
    assert len(github_transcription) > 0

    start_time = time.time()
    gemini_transcription = await gemini_model.speech_to_text(audio_path)
    gemini_time = time.time() - start_time
    assert isinstance(gemini_transcription, str)
    assert len(gemini_transcription) > 0

    print(f"GitHub speech-to-text time: {github_time:.2f}s")
    print(f"Gemini speech-to-text time: {gemini_time:.2f}s")


@pytest.mark.asyncio
async def test_text_to_speech(github_model, gemini_model):
    text = "This is a test sentence for text-to-speech conversion."
    output_path_github = "path/to/output/github_audio.wav"
    output_path_gemini = "path/to/output/gemini_audio.wav"

    start_time = time.time()
    github_audio_path = await github_model.text_to_speech(text, output_path_github)
    github_time = time.time() - start_time
    assert isinstance(github_audio_path, str)
    assert os.path.exists(github_audio_path)

    start_time = time.time()
    gemini_audio_path = await gemini_model.text_to_speech(text, output_path_gemini)
    gemini_time = time.time() - start_time
    assert isinstance(gemini_audio_path, str)
    assert os.path.exists(gemini_audio_path)

    print(f"GitHub text-to-speech time: {github_time:.2f}s")
    print(f"Gemini text-to-speech time: {gemini_time:.2f}s")


if __name__ == "__main__":
    pytest.main([__file__])
