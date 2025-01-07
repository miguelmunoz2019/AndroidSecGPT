import pandas as pd
from sacrebleu import corpus_bleu
from rouge_score import rouge_scorer
import bert_score
from openpyxl import load_workbook

# Leer el archivo Excel
file_path = "QuestionsSolvedAndroidSecGPT.xlsx" 
df = pd.read_excel(file_path)

# Inicializar las listas para almacenar los resultados de las métricas
bleu_scores = []
rouge_lp_scores = []
rouge_lr_scores = []
rouge_lf_scores = []
bert_scores_p = []
bert_scores_r = []
bert_scores_f = []

# Inicializar Rouge Scorer
rouge_scorer_tool = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)

# Calcular métricas para cada par de respuestas
for index, row in df.iterrows():
    print("--------------------Start------------------")
    official_answer = str(row['Official Answer'])
    print(official_answer)
    print("--------------------MID------------------")
    obtained_answer = str(row['Generated Answer'])
    print(obtained_answer)
    print("--------------------End------------------")
    
    # Calcular BLEU
    bleu = corpus_bleu([obtained_answer], [[official_answer]]).score
    bleu_scores.append(bleu)
    
    # Calcular ROUGE-L
    rouge_lp = rouge_scorer_tool.score(official_answer, obtained_answer)['rougeL'].precision
    rouge_lp_scores.append(rouge_lp)
    rouge_lr = rouge_scorer_tool.score(official_answer, obtained_answer)['rougeL'].recall
    rouge_lr_scores.append(rouge_lr)
    rouge_lf = rouge_scorer_tool.score(official_answer, obtained_answer)['rougeL'].fmeasure
    rouge_lf_scores.append(rouge_lf)
    
    # Calcular BERT-score
    bert_score_result = bert_score.score([obtained_answer], [official_answer], lang="en")
    bert_p = bert_score_result[0].item()
    print("--------------------Precision------------------")
    print(bert_p)
    bert_r = bert_score_result[1].item()  
    print("--------------------Recall------------------")
    print(bert_p)
    bert_f1 = bert_score_result[2].item()  
    print("--------------------F1------------------")
    print(bert_p)
    bert_scores_p.append(bert_p)
    bert_scores_r.append(bert_r)
    bert_scores_f.append(bert_f1)

# Agregar las métricas al DataFrame
df['BLEU'] = bleu_scores
df['ROUGE-L_Precision'] = rouge_lp_scores
df['ROUGE-L_Recall'] = rouge_lr_scores
df['ROUGE-L_FMeassure'] = rouge_lf_scores
df['BERT-score-precision'] = bert_scores_p
df['BERT-score-recall'] = bert_scores_r
df['BERT-score-f1'] = bert_scores_f

# Guardar el DataFrame con las nuevas columnas en el archivo Excel
with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
    df.to_excel(writer, index=False, sheet_name="Resultados_con_metricas")

print("Cálculo de métricas completado y resultados guardados en el archivo Excel.")

