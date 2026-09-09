# S.P.E.C.T.R.A. — Contexto do Projeto

## 1. Visão Geral e Propósito
O **S.P.E.C.T.R.A.** (*Stellar Parameter Estimation and Calculation Tools for Research and Analysis*) é uma suíte de software científico de alto desempenho para a astrofísica estelar. Disponibilizado tanto como aplicação gráfica desktop (GUI moderna com temas claro e escuro) quanto como CLI/REPL interativo (`spectra -e`), o sistema é projetado para estimar parâmetros fundamentais de estrelas pré-sequência principal (PMS) e de campo — em especial **massa estelar ($M_\odot$)**, **idade (Myr)**, **temperatura efetiva ($T_{\text{eff}}$)**, **luminosidade bolométrica ($\log_{10}(L/L_\odot)$)**, **gravidade superficial ($\log g$)** e **raio ($R_*/R_\odot$)**.

---

## 2. Pilha Tecnológica e Dependências
- **Linguagem**: Python 3.10+.
- **Interface Gráfica**: Tkinter / CustomTkinter com temas personalizados (*Spectra Deep Space Dark* e *Spectra Stellar Light*).
- **Computação Científica & Estatística**: NumPy, SciPy, Astropy, Pandas.
- **Machine Learning**: Scikit-Learn (Random Forest, Gradient Boosting, SVR, KNN, Bayesian Ridge, ElasticNet).
- **Visualização & Relatórios**: Matplotlib, Seaborn, Jinja2 / DataTables para geração de relatórios HTML interativos com gráficos em Base64.
- **Modelos Evolutivos Suportados**: Grids MADYS (18+ modelos teóricos, incluindo Siess 2000, BHAC15, PARSEC, MIST, Baraffe) com suporte a até 127+ filtros fotométricos.

---

## 3. Estrutura de Diretórios e Arquivos-Chave

```text
spectra/
├── main.py                     # Ponto de entrada da aplicação GUI / CLI
├── setup.py                    # Script de instalação e configuração do pacote Python
├── pyproject.toml              # Metadados e dependências do projeto
├── README.md                   # Documentação detalhada em inglês com histórico de versões
├── Manual.md                   # Manual técnico e teórico de operação do usuário
├── spectra/                    # Pacote Python principal
│   ├── gui/                    # Telas, abas (IsocFit, Primary, Regression, Math) e temas
│   ├── core/                   # Algoritmos de ajuste bayesiano 2D, cálculo de luminosidade e IMF
│   ├── models/                 # Gerenciador de grids MADYS e isócronas evolutivas
│   ├── ml/                     # Modelos de regressão e pipelines de imputação (KNN, MICE)
│   └── reports/                # Geradores de relatórios HTML e diagramas HR/CMD
├── isochrone_models/           # Grids de isócronas baixadas e instaladas localmente
├── outputs/                    # Diretório estruturado de exportação de resultados:
│   ├── isochrone_fitting/      # Tabelas de ajuste bayesiano e diagramas HRD
│   ├── primary_parameters/     # Parâmetros primários, diagnósticos T Tauri (CTTS/WTTS)
│   ├── mass_modeling/          # Relatórios e dashboards de regressão massa-magnitude
│   └── math_models/            # Matrizes de correlação, PCA e dados imputados
├── publishing/                 # Pacote de publicação para manuscrito MNRAS / LaTeX
└── tests/                      # Bateria de testes unitários e de integração
```

---

## 4. Principais Módulos do Sistema
1. **2D Bayesian Isochrone Fitting (`IsocFit`)**:
   - Ajuste em grade 2D de probabilidade no diagrama HR considerando incertezas observacionais e funções de massa inicial (IMF Salpeter/Kroupa).
2. **Primary Stellar Parameters Module**:
   - Conversões fotométricas baseadas em Bell et al. (2014, MNRAS 444, 1157), diagnósticos de juventude via larguras equivalentes de $H\alpha$, $Li\,\text{I}$ e $TiO$.
3. **Mass–Magnitude Regression Modeling**:
   - Treinamento e benchmark de 10+ regressores comparando magnitudes (`G`, `J`, `H`, `K`) com massas teóricas.
4. **Mathematical Modeling & Feature Engineering**:
   - Imputação multivariada de valores faltantes (`KNN`, `Iterative`), PCA e seleção de features.
5. **Interactive Reports & Batch Pipeline**:
   - Execução em lote para pastas com múltiplos aglomerados estelares (`spectra batch --dir ...`).

---

## 5. Como Executar e Desenvolver
- **Executar Interface Gráfica (Desktop GUI)**:
  ```bash
  python main.py
  # ou (se instalado via pip/conda):
  spectra
  ```
- **Executar CLI / REPL Interativo**:
  ```bash
  spectra -e
  ```
- **Executar Processamento em Lote**:
  ```bash
  spectra batch --dir caminho/para/aglomerados/ --model Siess2000
  ```
