# Small language models

## SLM versus LLM
- Language models process/generate text; **parameters** are learned numerical weights, distinct from training tokens. “Small” is relative—no universally fixed cutoff.
| SLM tendency | Trade-off |
| --- | --- |
| Fewer parameters / compact architecture | Lower memory/compute, possible on-device operation |
| Curated data / task adaptation | Efficient target tasks; narrower coverage can limit generalisation |
| Local deployment | Lower network dependence and potential privacy benefits, subject to device/data security |
| Smaller scale | May struggle with broad factual knowledge/complex tasks; still can hallucinate or inherit bias |
- Source contrasts SLMs with **GPT-3**, a dated scale example; not a benchmark proving all small models inferior on every task.
- Quality of data, architecture, training and evaluation matter as well as size. SLMs are not necessarily trained only for one narrow task or on tiny datasets; a model may be general-purpose and then adapted.
- Example **Phi-3-mini**, **3.8 bn parameters**, **3.3 trillion training tokens**, demonstrates on-phone potential; example not a recommended product/current benchmark ranking. [Microsoft primary report](https://www.microsoft.com/en-us/research/publication/phi-3-technical-report-a-highly-capable-language-model-locally-on-your-phone/?lang=fr_ca).
- Use cases: constrained devices, task-specific assistants and local text processing; evaluate accuracy, latency, energy, privacy and failure handling in the intended setting.

## PDF coverage

2025-01-17: pp. 16, 17
