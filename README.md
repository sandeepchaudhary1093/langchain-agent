conda create -n langagent python=3.11 -y

conda activate langagent

pip install -r requirements.txt

Create a `.env` file in the project root with your API keys:

```env
OPENAI_API_KEY=your-openai-api-key
TAVILY_API_KEY=your-tavily-api-key
WEATHERSTACK_API_KEY=your-weatherstack-api-key
```

Start the chat interface:

```bash
streamlit run main.py
```