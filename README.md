# ThinkFlow
Use the CoT (Chain of Thought) model to guide non - reasoning models and improve the quality of dialogue.
A conversational pipeline designed for Open WebUI. It leverages the Chain of Thought (CoT) model to guide non-reasoning AI systems, enhancing dialogue quality through a two-stage process:
1. **R1 Reasoning**: Uses the `deepseek-reasoner` model for logical inference
2. **V3 Response**: Generates final responses with `deepseek-chat`, incorporating the reasoning results

Key features:
- Async streaming support
- Configurable temperature parameters for both stages
- Integration with DeepSeek's dual-engine architecture
- Automatic CoT reasoning injection into response generation

The pipeline processes user input through:
1. Reasoning phase (R1) with structured thought generation
2. Response generation phase (V3) using augmented context
This architecture allows non-reasoning models to benefit from explicit logical reasoning while maintaining natural conversational flow.
