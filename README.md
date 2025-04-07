# Prompt Library Organization and Filtering with Local LLM (Ollama and LLAMA 3.2)

This project demonstrates how to use a local LLM (specifically Ollama and LLAMA 3.2) to perform basic organization and filtering of a prompt library. The primary use case is to prepare a prompt library for open-sourcing by removing personally identifiable information (PII) and categorizing the prompts.

## Functionality

The project implements the following functionalities:

1.  **PII Filtering:** The system allows a user to define PII using text and filter keywords. Prompts containing these keywords are flagged for removal. This is implemented with basic scripting for simplicity and direct control.
2.  **Categorization:** The project supports category creation for prompts. Either the user defines a list of categories or the LLM is tasked with building the list. Prompts are then scanned and assigned to appropriate categories. Prompts flagged in the PII filtering stage are not passed into the cleaned, categorized output.

## Basic Usage

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```
2.  **Set up Ollama with Llama 3.2:**
    Ensure you have [`Ollama`](https://ollama.com/) installed and that the `Llama 3.2` model is available.
3.  **Run the filtering and categorization scripts:**
    Execute the scripts provided in the repository to filter and categorize your prompt library. Refer to the script documentation for specific instructions on defining PII and categories.
4.  **Review the output:**
    Inspect the cleaned output directory to find your categorized prompts, with PII-flagged prompts removed.

## Further Enhancements

The current implementation provides a basic structure that can be expanded upon. Some potential enhancements include:

*   **Prompt Generalization:** Use Ollama or local LLMs to rewrite personalized prompts (e.g., prompts tailored for a specific individual) into more general and universally applicable versions. This can be integrated into the workflow to automatically generalize prompts before categorization.
*   **Enhanced PII Detection:** Employ more sophisticated PII detection methods beyond simple keyword matching.
*   **Automated Category Generation**: Implement automated methods for category generation based on prompt content.

 