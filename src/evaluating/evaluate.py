import json


def evaluator(my_answers_path: str, ref_answers_path: str) -> None:
    with open(my_answers_path, "r") as f:
        my_file = json.load(f)
    with open(ref_answers_path, "r") as f:
        reference_file = json.load(f)

    recall_lst = [1, 3, 5, 10]

    # pour chaque chiffre de la chiffre on va faire un recall si on peut
    # on envoie les k premiers chunks a la fonction recall
    # on envoie aussi la source de référence


def recall() -> None:
    pass


# EXEMPLE DE REFERENCE
# ON VA IMAGINER QU'IL PUISSE Y AVOIR PLUSIEURS REFERENCES DANS SOURCES

# {
#   "rag_questions": [
#     {
#       "question_id": "189c8b8a-e59c-4fca-92ad-c02df42cbe40",
#       "question": "What activation formats does the fused batched MoE layer return in vLLM?",
#       "answer": "The fused batched MoE layer returns a tuple of two `mk.FusedMoEActivationFormat.BatchedExperts` values from its `activation_formats` property.",
#       "sources": [
#         {
#           "file_path": "data/raw/vllm-0.10.1/vllm/model_executor/layers/fused_moe/fused_batched_moe.py",
#           "first_character_index": 28416,
#           "last_character_index": 28975
#         }
#       ],
#       "difficulty": "synthetic",
#       "is_valid": true
#     },

# EXEMPLE DE MON FICHIER
# PRENDRE DANS RETRIEVED SOURCES LES K PREMIERS CHUNKS

# {
#     "search_results": [
#         {
#             "question_id": "189c8b8a-e59c-4fca-92ad-c02df42cbe40",
#             "question": "What activation formats does the fused batched MoE layer return in vLLM?",
#             "retrieved_sources": [
#                 {
#                     "file_path": "data/raw/vllm-0.10.1/docs/design/fused_moe_modular_kernel.md",
#                     "first_character_index": 0,
#                     "last_character_index": 1786
#                 },
#                 {
#                     "file_path": "data/raw/vllm-0.10.1/vllm/lora/models.py",
#                     "first_character_index": 1888,
#                     "last_character_index": 2340
#                 },
#                 {
#                     "file_path": "data/raw/vllm-0.10.1/vllm/model_executor/layers/quantization/compressed_tensors/compressed_tensors_moe.py",
#                     "first_character_index": 16237,
#                     "last_character_index": 17544
#                 },
#                 {
#                     "file_path": "data/raw/vllm-0.10.1/docs/getting_started/installation/cpu.md",
#                     "first_character_index": 9439,
#                     "last_character_index": 9927
#                 },
#                 {
#                     "file_path": "data/raw/vllm-0.10.1/vllm/model_executor/layers/quantization/quark/quark_moe.py",
#                     "first_character_index": 11876,
#                     "last_character_index": 13684
#                 },
#                 {
#                     "file_path": "data/raw/vllm-0.10.1/tests/kernels/moe/modular_kernel_tools/cli_args.py",
#                     "first_character_index": 2445,
#                     "last_character_index": 3770
#                 },
#                 {
#                     "file_path": "data/raw/vllm-0.10.1/vllm/model_executor/layers/quantization/gguf.py",
#                     "first_character_index": 19972,
#                     "last_character_index": 21198
#                 },
#                 {
#                     "file_path": "data/raw/vllm-0.10.1/vllm/model_executor/layers/quantization/modelopt.py",
#                     "first_character_index": 62096,
#                     "last_character_index": 63054
#                 },
#                 {
#                     "file_path": "data/raw/vllm-0.10.1/vllm/model_executor/layers/fused_moe/fused_batched_moe.py",
#                     "first_character_index": 0,
#                     "last_character_index": 877
#                 },
#                 {
#                     "file_path": "data/raw/vllm-0.10.1/vllm/model_executor/layers/quantization/utils/flashinfer_fp4_moe.py",
#                     "first_character_index": 1836,
#                     "last_character_index": 3230
#                 }
#             ],
#             "answer": "vLLM CPU supports quantizations such as AWQ, GPTQ, and compressed-tensor INT8 W8A8."
#         },
