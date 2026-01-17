# GEMINI.md

## Directory Overview

This directory contains educational materials for a lecture on **Introduction to Technical Thermodynamics**. The content is authored by dr hab. inż. prof. UPP Marek Urbaniak and is prepared in Polish.

The project uses [Quarto](https://quarto.org/) to create a `reveal.js` presentation from a source `.qmd` file.

## Key Files

*   `01_Wprowadzenie.qmd`: The main source file for the presentation. It is written in Quarto's extended Markdown format and includes lecture content, formatting directives, and embedded R code chunks for generating plots.
*   `01_Wprowadzenie.html`: The final, rendered HTML presentation. This file is self-contained and can be opened in any web browser.
*   `01_Wprowadzenie_files/`: A directory containing all the necessary assets (JavaScript libraries, CSS, images) for the HTML presentation to function correctly.

## Usage

The primary purpose of this directory is to serve as the source for a university lecture.

*   **Viewing the Presentation:** Open the `01_Wprowadzenie.html` file in a web browser.
*   **Editing the Content:** Modify the `01_Wprowadzenie.qmd` file.
*   **Rendering the Presentation:** To apply changes made to the `.qmd` file, you need to have Quarto installed and run the following command in the terminal:

    ```bash
    quarto render 01_Wprowadzenie.qmd
    ```

This will regenerate the `01_Wprowadzenie.html` file and update the contents of the `01_Wprowadzenie_files/` directory.
