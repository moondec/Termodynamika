import xml.etree.ElementTree as ET
import re

def process_zadania():
    tree = ET.parse('egzamin_zadania.xml')
    root = tree.getroot()

    for q in root.findall(".//question"):
        qtype = q.get('type')
        if qtype == 'calculated':
            name_node = q.find("name/text")
            if name_node is not None:
                name_node.text = "Zadanie obliczeniowe"
                
            qtext_node = q.find("questiontext/text")
            if qtext_node is not None:
                text = qtext_node.text
                
                # Remove title paragraph e.g. <p><b>Zadanie 1 — Ogrzewanie gazu</b></p>
                text = re.sub(r"<p><b>Zadanie\s+\w+[a-z]?\s*—\s*[^<]+</b></p>", "", text)
                
                # Remove "(kontynuacja Zadania X)"
                text = re.sub(r"\(kontynuacja Zadania\s+\w+[a-z]?\)\s*", "", text)
                
                # Add TH and TL if it's the skraplacz task (Zad03b)
                if "Moc elektryczna bloku wynosi" in text:
                    addition = "<p>Siłownia parowa pracuje między temperaturą <b>{TH}</b> °C (kocioł) a temperaturą wody chłodzącej <b>{TL}</b> °C (skraplacz).</p>"
                    text = addition + text
                    
                qtext_node.text = text

    tree.write('egzamin_zadania_niezalezne.xml', encoding='utf-8', xml_declaration=True)
    print("egzamin_zadania_niezalezne.xml created.")

def process_teoria():
    tree = ET.parse('egzamin_teoria.xml')
    root = tree.getroot()

    for q in root.findall(".//question"):
        qtype = q.get('type')
        if qtype in ['multichoice', 'truefalse']:
            name_node = q.find("name/text")
            if name_node is not None:
                name_node.text = "Pytanie teoretyczne"
                
            qtext_node = q.find("questiontext/text")
            if qtext_node is not None:
                text = qtext_node.text
                # Remove numbering e.g. <b>P1.</b>
                text = re.sub(r"<b>P\d+\.</b>\s*", "", text)
                qtext_node.text = text

    tree.write('egzamin_teoria_niezalezne.xml', encoding='utf-8', xml_declaration=True)
    print("egzamin_teoria_niezalezne.xml created.")

process_zadania()
process_teoria()
