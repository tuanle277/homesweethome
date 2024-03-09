"""## Feature analysis using LLM"""

from transformers import pipeline

def generate(task):
  # Initialize the text generation pipeline with GPT-2
  generator = pipeline(task, model='gpt2')

  aspects = ["school", "safety", "quiet", "friendliness of the people"]

  def generate_review(prompt):
    generated_text = generator(prompt, max_length=200, num_return_sequences=1)

    # Print the generated summary
    print(generated_text[0]['generated_text'])

  def analyze_aspect_sentiments(review, aspects):

    for aspect in aspects:
        if aspect in review.lower():
            # Perform sentiment analysis on the sentence containing the aspect.
            prompt = f"Summarize the following review about a neighborhood focusing on key aspects such as {', '.join(aspects)}. Provide a concise overview that captures the essence of the review in a few sentences: {review}"
            generate_review(prompt)
    print("\n")

  for home in home_data:
    analyze_aspect_sentiments(home["Listing Remarks"], aspects)
