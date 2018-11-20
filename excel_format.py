import pandas as pd
import datetime
import math


document_prefix = 'FA'
procent_tva = ['24']
company_sufix = 'SRL'

def format_csv(input = 'JurnalVanzari.csv', output = 'Output.csv'):
    with open(input, 'r') as content_file:
        content = content_file.read()
    print('Content read')
    content_list = content.split(",")
    print('Split done')
    no_blanks = []
    for elem in content_list:
        if elem != "" and elem != "nan" and elem:
            no_blanks.append(elem)
    print('Blanks cleared done')
#    print(no_blanks)
    string_no_blanks = ",".join(no_blanks)
    string_no_blanks = string_no_blanks.replace("\n,\n", "\n")
    string_no_blanks = string_no_blanks.replace("\n,\n", "\n")
    string_no_blanks = string_no_blanks.replace("\n,\n", "\n")
#    print(string_no_blanks)
    with open(output, "w") as text_file:
        text_file.write(string_no_blanks)
    print('CSV created')
    return string_no_blanks

def is_date(date_text):
    try:
        if '\n' in date_text:
            date_text = date_text[1:]
        datetime.datetime.strptime(date_text, '%d-%b-%Y').strftime('%d-%b-%Y')
        return True
    except ValueError:
        return False


def is_doc(string):
    if document_prefix in string:
        return True
    return False

def is_company(string):
    if company_sufix in string:
        return True
    return False

def is_value_no_tva(precedent):
    if is_company(precedent):
        return True
    return False

def is_product(precedent):
    if (not isFloat(precedent)) and precedent in procent_tva:
        return True
    return False

def isFloat(string):
    if string[-3:] == '.00':
        return True
    return False

if __name__ == "__main__":
    str_formatted = format_csv()
    csv = str_formatted.split(",")
    csv[12] = csv[12][5:]
    csv = csv[12:]
    precedent = ""
    row_comp = ()
    row_produs = ()
    data, doc, companie, value_no_tva, tva, value_with_tva, cost = (), (), (), (), (), (), ()
    produs, quantity, product_pret_unitar, product_total_value, product_cost = (), (), (), (), ()
    case = "none"
    found_new = False
    row_list = []
    for item in range(len(csv)):
        elem = csv[item]
        # Trebuie sa verific daca pot accesa inainte sa le atribui
        precedent = csv[item-1]
        second_precedent = csv[item-2]
        third_precedent = csv[item-3]
        fourth_precedent = csv[item-4]
        fifth_precedent = csv[item-5]

        if is_date(elem):
            data = (elem[1:],)
        if is_doc(elem):
            doc = (elem,)

        if is_company(elem):
            companie = (elem,)
            case = "gasit_companie"
        elif is_product(precedent):# Transmit precedentul pentru a verifica daca este valoarea TVA, daca DA atunci campul curent este produs
            produs = (elem,)
            case = "gasit_produs"

        if case == "gasit_companie":
            if is_value_no_tva(precedent):# Transmit precedentul pentru a verifica daca este companie
                value_no_tva = (elem,)#Poate fi si cu precedent = produs
            if is_value_no_tva(second_precedent):# Second_precedent trebuie sa fie companie / produs pentru a identifica campul curent drept valoare TVA
                tva = (elem,)
            if is_value_no_tva(third_precedent): # Third_precedent trebuie sa fie companie / produs pentru a identifica campul curent drept valoare cu TVA
                value_with_tva = (elem,)
            if is_value_no_tva(fourth_precedent): # Fourth_precedent trebuie sa fie companie / produs pentru a identifica campul curent drept COST
                temp = elem[:-1]
                temp = float(temp)
                cost = (temp,)

        elif case == "gasit_produs":
            if isFloat(elem) and is_product(second_precedent):# Transmit second_precedent pentru a verifica daca este valoare TVA, daca da PRECEDENTUL este produs, deci curentul este cantitate
                quantity = (elem,)
            if is_product(third_precedent): # Transmit THIRD_PRECEDENT pentru a verifica daca este valoare TVA, daca da SECOND_PRECEDENT este produs, deci curentul este valoare pret unitar
                product_pret_unitar = (elem,)
            if is_product(fourth_precedent): # Transmit FOURTH_PRECEDENT pentru a verifica daca este valoare TVA, daca da THIRD_PRECEDENT este produs, deci curentul este valoare totala
                product_total_value = (elem,)
            if is_product(fifth_precedent): # Transmit FIFTH_PRECEDENT pentru a verifica daca este valoare TVA, daca da FOURTH_PRECEDENT este produs, deci curentul este cost
                product_cost = (elem,)
                found_new = True

        row_comp = data + doc + companie + value_no_tva + tva + value_with_tva + cost
        if produs != () and product_cost != () and found_new == True:
            row_produs = row_comp + produs + quantity + product_pret_unitar + product_total_value + product_cost
            row_list.append(row_produs)
            found_new = False

    dataframe = pd.DataFrame(row_list, columns=['Data', 'Document', 'Companie', 'Valoare_doc_fara_tva',
                                                'Valoare_doc_tva', 'Valoare_doc_cu_tva', 'Cost_total_doc', 'Produs',
                                                'Produs_cantitate', 'Produs_pret_unitar', 'Produs_valoare_totala',
                                                'Produs_cost'])
    dataframe.to_csv('Dataframe.csv', sep=',', encoding='utf-8')
    print('Done')
