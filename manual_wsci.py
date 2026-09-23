from pathlib import Path
from ollama import chat


question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

selected_files = [
    Path("knowledge/wifi_setup.txt"),
    Path("knowledge/password_changes.txt"),
    Path("knowledge/service_status.txt"),
]


context = ""

## Write a for loop to go through all the files in selected_files and read their contents into the context variable.
for file in selected_files:
    context += file.read_text()
    context += "\n\n"


## Call Qwen with the student's question and the context you created above.
response = chat(
    model="qwen2.5:3b",
    messages=[
        {
            "role": "user",
            "content": (
                "Answer the student's question using only the relevant context below. "
                "Give clear troubleshooting steps.\n\n"
                "Student question:\n" + question +
                "\nRelevant context:\n" + context
            ),
        }
    ],
)



print(
    "Context characters:",
    len(context)
)
print(response.message.content)
