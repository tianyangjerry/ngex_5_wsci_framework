from pathlib import Path
from ollama import chat
import json



question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

## WRITE ##
service_status = {
    "wifi": "operational"
}

state = {
    "problem": question,
    "device": "Windows laptop",
    "wifi_status": service_status["wifi"],
    "wifi_check": True
}

with open("state.json", "w") as file:
    json.dump(
        state,
        file,
        indent=2
    )

with open("state.json", "r") as file:
    state = json.load(file)

print(state)


## SELECT CONTEXT FILES BASED ON QUESTION
## Create the function that takes the student's question, takes some keywords and chooses the relevant files from the knowledge base. Return a list of the selected files.
## For example, if the question has the kyeword "print" or "printer", then the function should return the file "knowledge/printer_setup.txt" in a list.
def select_context(question):
    question = question.lower()
    selected_files = []

    file_keywords = {
        "knowledge/wifi_setup.txt": ["wifi", "wi-fi", "wireless", "eduroam"],
        "knowledge/password_changes.txt": ["password", "credential", "sign in"],
        "knowledge/service_status.txt": ["status", "outage", "operational", "wifi", "wi-fi", "eduroam"],
        "knowledge/vpn.txt": ["vpn"],
        "knowledge/email_setup.txt": ["email", "mail"],
        "knowledge/printing.txt": ["print", "printer", "printing"],
        "knowledge/classroom_projectors.txt": ["projector", "display", "hdmi"],
    }

    for file_name, keywords in file_keywords.items():
        for keyword in keywords:
            if keyword in question:
                selected_files.append(Path(file_name))
                break

    return selected_files


selected_files = select_context(question)

## READ SELECTED FILES and add their contents to the context variable.
context = ""

for file in selected_files:
    context += file.read_text()
    context += "\n\n"


## 
## COMPRESS CONTEXT
## Add logic to compress the context from above by calling Qwen with "context" and the "question" as the parameter
## The response from Qwen should be the compressed context. Store it in a variable called "compressed_context" 

def compress_context(context, question):
    response = chat(
        model="qwen2.5:3b",
        messages=[
            {
                "role": "system",
                "content": "Use only the provided context. Do not invent steps, sources, commands, or facts.",
            },
            {
                "role": "user",
                "content": (
                    "Extract only the facts needed to answer the student's question. "
                    "Keep the result short and do not add new information.\n\n"
                    "Student question:\n" + question +
                    "\nContext:\n" + context
                ),
            }
        ],
    )
    return response.message.content


compressed_context = compress_context(context, question)



## Print the length of the compressed context
print(len(compressed_context))

## Now, call Qwen again with the compressed context and the student's question. Store the response in a variable called "response" and print the response from Qwen.
## Ensure the model produces a structured output 
response = chat(
    model="qwen2.5:3b",
    format="json",
    messages=[
        {
            "role": "user",
                "content": (
                    "Return a JSON object with these keys: problem, diagnosis, steps, "
                    "and sources. The steps must be a list of strings. The sources "
                    "must contain only the supplied file names. Use only the provided "
                    "context. Do not add troubleshooting steps that are not in it.\n\n"
                    "Supplied file names:\n" +
                    "\n".join(str(file) for file in selected_files) +
                    "\n\n"
                    "Student question:\n" + question +
                "\nCompressed context:\n" + compressed_context
            ),
        }
    ],
)


## WRITE the above output in an artifact called "state"
answer = json.loads(response.message.content)
answer["sources"] = [str(file) for file in selected_files]
state["answer"] = answer
state["selected_files"] = [str(file) for file in selected_files]
state["compressed_context"] = compressed_context

print(json.dumps(answer, indent=2))

with open("state.json", "w") as file:
    json.dump(state, file, indent=2)

## Update the rest of the code so that it uses the "state" artifact as part of the context. 
## It is important to ensure that the model uses only the relevant parts from the "state" artifact and not the entire artifact.
## For this, you may have to think of a good structure for the "state" artifact and how to use it in the context.
with open("state.json", "r") as file:
    saved_state = json.load(file)

diagnostic_context = {
    "problem": saved_state["problem"],
    "device": saved_state["device"],
    "wifi_status": saved_state["wifi_status"],
    "diagnosis": saved_state["answer"]["diagnosis"],
    "steps": saved_state["answer"]["steps"],
}

final_response = chat(
    model="qwen2.5:3b",
    messages=[
        {
            "role": "system",
            "content": "Use only the diagnostic context. Do not add facts or steps. Only discuss the Windows laptop.",
        },
        {
            "role": "user",
            "content": (
                "Give the student a concise final answer using only this diagnostic "
                "context. Do not mention the internal state file. Ignore any steps "
                "for other operating systems or devices.\n\n" +
                json.dumps(diagnostic_context, indent=2)
            ),
        }
    ],
)

print(final_response.message.content)


