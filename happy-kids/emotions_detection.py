# Import necessary libraries
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from torch.nn.functional import softmax
import seaborn as sns
import matplotlib.pyplot as plt

label_emotions = [ "sadness", "joy", "love", "anger", "fear", "surprise"]

# Load the model and tokenizer
model_name = "TieIncred/distilbert-base-uncased-finetuned-emotional"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Get emotion labels in original order
id2label = model.config.id2label
emotions_order = [id2label[i] for i in range(len(id2label))]

# Function to classify text and show all emotion probabilities
def classify_emotions(text):
    # Tokenize the input
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    
    # Get model prediction
    with torch.no_grad():
        outputs = model(**inputs)
    # Store the prediction history
    if not hasattr(classify_emotions, 'history'):
        classify_emotions.history = {emotion: [] for emotion in emotions_order}
    
    # Get probabilities for current prediction
    probs = softmax(outputs.logits, dim=1)[0].tolist()
    
    # Update history with new probabilities
    for emotion, prob in zip(emotions_order, probs):
        classify_emotions.history[emotion].append(prob)
    
    # Convert logits to probabilities
    probs = softmax(outputs.logits, dim=1)[0].tolist()
    
    # Return emotions with probabilities in the fixed order
    return {emotion: probs[i] for i, emotion in enumerate(emotions_order)}

# Function to create ASCII bar chart
def create_bar(probability, max_width=40):
    bar_width = int(probability * max_width)
    return '*' * bar_width

# Main loop
print("Enter text to analyze emotions. Type 'END' to quit.")
print("-" * 60)



while True:
    text = input("\nEnter text: ")
    
    if text.upper() == "END":
        print("\nThank you for using the emotion analyzer!")
        break
    
    print("-" * 60)
    
    emotions = classify_emotions(text)
    
    # Display results with ASCII bar charts
    # Store emotion probabilities for final plot
    for i, emotion in enumerate(emotions_order):
        probability = emotions[emotion]
        bar = create_bar(probability)
        print(f"{label_emotions[i].ljust(10)}: {probability:.4f} ({probability*100:.1f}%) {bar}")
        # Initialize emotion_histories if not already defined
        if 'emotion_histories' not in locals():
            emotion_histories = {emotion: [] for emotion in emotions_order}
        # Add probability to emotion's history
        emotion_histories[emotion].append(probability)

# Create line plot if we have more than 1 data point
if len(classify_emotions.history[emotions_order[0]]) > 1:
    
    # Clear previous plot
    plt.clf()
    
    # Create the line plot
    for emotion in emotions_order:
        sns.lineplot(data=classify_emotions.history[emotion], label=label_emotions)
        
    # Save plot as PNG file
    plt.title('Emotion Probabilities Over Time')
    plt.xlabel('Input Number')
    plt.ylabel('Probability')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('static/emotion_trends.png', bbox_inches='tight', dpi=300)

    # Generate HTML page
    # Convert emotion histories to JSON format for JavaScript
    emotion_data = {emotion: classify_emotions.history[emotion] for emotion in emotions_order}
    emotion_labels = label_emotions
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Emotion Analysis Results</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 20px;
                background-color: #f5f5f5;
            }}
            .plot-container {{ 
                max-width: 90%;
                margin: 0 auto;
                padding: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            #plotDiv {{
                width: 100%;
                height: 600px;
            }}
            @media (max-width: 768px) {{
                .plot-container {{
                    max-width: 95%;
                    padding: 10px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="plot-container">
            <h1>Emotion Analysis Trends</h1>
            <div id="plotDiv"></div>
        </div>
        
        <script>
            const emotionData = {str(emotion_data)};
            const emotionLabels = {str(emotion_labels)};
            
            const traces = Object.keys(emotionData).map((emotion, index) => ({{
                y: emotionData[emotion],
                mode: 'lines',
                name: emotionLabels[index],
                line: {{width: 3}}
            }}));
            
            const layout = {{
                title: 'Emotion Probabilities Over Time',
                xaxis: {{title: 'Input Number'}},
                yaxis: {{title: 'Probability'}},
                hovermode: 'closest',
                showlegend: true,
                legend: {{
                    x: 1.05,
                    y: 1,
                    xanchor: 'left'
                }},
                margin: {{r: 150}}
            }};
            
            Plotly.newPlot('plotDiv', traces, layout);
        </script>
    </body>
    </html>
    """

    # Save HTML file
    with open('static/emotion_analysis.html', 'w') as f:
        f.write(html_content)
    
    # Display plot
    plt.pause(0.1)