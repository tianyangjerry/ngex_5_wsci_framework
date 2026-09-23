## This file is a bad way of managing context. 

from pathlib import Path
from ollama import chat


question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""


context = ""

for file in Path("knowledge").glob("*.txt"):
    context += file.read_text()
    context += "\n\n"

## Make a call to Qwen with student's question and the context from the knowledge base.
response = chat(
    model="qwen2.5:3b",
    messages=[
        {
            "role": "user",
            "content": (
                "Answer the student's question using the knowledge base below. "
                "Give clear troubleshooting steps.\n\n"
                "Student question:\n" + question +
                "\nKnowledge base:\n" + context
            ),
        }
    ],
)



## Just for fun, print the total length of the context
print(
    "Context characters:",
    len(context)
)

## Print the response from Qwen
print(response.message.content)
