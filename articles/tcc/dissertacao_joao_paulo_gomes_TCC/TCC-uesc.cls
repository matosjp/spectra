%
% Classe ppgmc-uesc.cls para o Programa de Pós-Graduação em Modelagem Matemática e Computacional baseada na classe abntex da ABNT
%by: Valdex de Jesus Santos <vjsantos@uesc.br>
%
%	Dependência: abntex2 >= 1.7
%
%	Agradecimentos:
%		------ <email>
%	


\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ppgmcuesc}[2014/1/24 v1.0]

% repassa os parametros ao abntex2
\DeclareOption*{
	\PassOptionsToClass{\CurrentOption}{abntex2}
}

\PassOptionsToClass{
	% -- opções da classe memoir --
	12pt,				% tamanho da fonte
	openright,			% capítulos começam em pág ímpar (insere página vazia caso preciso)
	a4paper,			% tamanho do papel.
	%sumario=tradicional, % seleciona o sumário tradicional
	% -- opções da classe abntex2 --
	chapter=TITLE,			% títulos de capítulos convertidos em letras maiúsculas
	%section=TITLE,			% títulos de seções convertidos em letras maiúsculas
	%subsection=TITLE,		% títulos de subseções convertidos em letras maiúsculas
	%subsubsection=TITLE,		% títulos de subsubseções convertidos em letras maiúsculas
	% -- opções do pacote babel --
	brazil,				% o último idioma é o principal do documento
	}{abntex2}

\ProcessOptions\relax
\LoadClass{abntex2}

\RequirePackage{chngcntr}

% define a numeração das equações de forma sequencial
\counterwithout{equation}{chapter}

%\counterwithout{equacao}{chapter}



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% ESTILO DE ELEMENTOS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% elementos pre-textuais
\renewcommand{\pretextual}{

    \pagenumbering{arabic} % algarismos arabicos
    \aliaspagestyle{chapter}{empty}%tira a numeração dos elementos pré-textuais
	\pagestyle{empty} 
	\aliaspagestyle{cleared}{empty}
	\aliaspagestyle{part}{empty}

	
}
\pagestyle{myheadings}

% elementos textuais
% Configura layout para elementos textuais
\renewcommand{\textual}{

	%\pagenumbering{arabic} % inicia a numeração em 1
	\ifthenelse{\equal{\ABNTEXisarticle}{true}}{
		\pagestyle{plain}
	}
		{
		\pagestyle{myheadings}
		\aliaspagestyle{chapter}{abntchapfirst}
	}
	\nouppercaseheads
	\bookmarksetup{startatroot}
}

% elementos pos-textuais

\renewcommand{\postextual}{
\setlength{\afterchapskip}{20pt}       %espaçamento entre titulo e referenc
\setlength{\bibitemsep}{12pt} %espaçamento entre referenc
\phantompart}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% COMANDOS DE DADOS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% comandos de dados - programa
\providecommand{\imprimirprograma}{}
\newcommand{\programa}[1]{\renewcommand{\imprimirprograma}{#1}}

% comandos de dados - subtítulo
\providecommand{\imprimirsubtitulo}{}
\newcommand{\subtitulo}[1]{\renewcommand{\imprimirsubtitulo}{#1}}

%comando de título em english
\providecommand{\imprimirtitleenglish}{}
\newcommand{\titleenglish}[1]{\renewcommand{\imprimirtitleenglish}{#1}}

% comandos de dados - instituição do orientador
\providecommand{\imprimirinstOrientador}{}
\newcommand{\instOrientador}[1]{\renewcommand{\imprimirinstOrientador}{#1}}

% comandos de dados - instituição do coorientador
\providecommand{\imprimirinstCoorientador}{}
\newcommand{\instCoorientador}[1]{\renewcommand{\imprimirinstCoorientador}{#1}}

% criação do comando para área de concentração (folha de rosto)
\newcommand{\imprimirareaconcentracaoRotulo}{\'Area de concentra\c{c}\~ao: }
\providecommand{\imprimirareaconcentracao}{}
\newcommand{\areaconcentracao}[1]{\renewcommand{\imprimirareaconcentracao}{#1}}

% criação do comando para linha de pesqusa (folha de rosto)
\newcommand{\imprimirlinhapesquisaRotulo}{Linha de pesquisa: }
\providecommand{\imprimirlinhapesquisa}{}
\newcommand{\linhapesquisa}[1]{\renewcommand{\imprimirlinhapesquisa}{#1}}

%========================================================================
%DADOS DA DEFFESA

%comando data de defesa
\providecommand{\imprimirdatadefesa}{}
\newcommand{\datadefesa}[1]{\renewcommand{\imprimirdatadefesa}{#1}}

%comandoS MEMBROS DA BANCA
%\providecommand{\imprimirbancamembrodois}{}
%\newcommand{\bancamembrodois}[1]{\renewcommand{\imprimirbancamembrodois}{#1}}
%\providecommand{\imprimirbancainstmembrodois}{}
%\newcommand{\bancainstmembrodois}[1]{\renewcommand{\imprimirbancainstmembrodois}{#1}}

\providecommand{\imprimirbancamembrointerno}{}
\newcommand{\bancamembrointerno}[1]{\renewcommand{\imprimirbancamembrointerno}{#1}}

\providecommand{\imprimirbancainstmembrointerno}{}
\newcommand{\bancainstmembrointerno}[1]{\renewcommand{\imprimirbancainstmembrointerno}{#1}}

\providecommand{\imprimirbancamembroexterno}{}
\newcommand{\bancamembroexterno}[1]{\renewcommand{\imprimirbancamembroexterno}{#1}}

\providecommand{\imprimirbancainstmembroexterno}{}
\newcommand{\bancainstmembroexterno}[1]{\renewcommand{\imprimirbancainstmembroexterno}{#1}}

%=======================================================================

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% OBJETOS FLUTUANTES
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% comando que trata a fonte nos objetos flutuantes
\renewcommand{\fonte}[1]{
	\\
	\centering\normalfont\footnotesize{Fonte: #1}
}

% comando que trata as notas nos objetos flutuantes
\renewcommand{\nota}[1]{
	\begin{SingleSpacing}\par\end{SingleSpacing}
	\begin{tabular}{p{.05\textwidth}p{.9\textwidth}}
		Nota: & #1
	\end{tabular}
}


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PARÁGRAFOS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% tamanho da identação do parágrafo
\setlength{\parindent}{1.5cm}

%espaçamento entre linhas
\renewcommand{\baselinestretch}{1.5}  


%% Espaçamentos nos títulos:
%% chapter
%\setlength{\beforechapskip}{-\onelineskip}
\setlength{\afterchapskip}{\onelineskip}           
%\setlength\beforechapskip{-18pt}
%\setlength{\afterchapskip}{20pt}
\setlength{\setaftersecskip}{\onelineskip}
\setlength{\setaftersubsecskip}{\onelineskip}


%
%% section
%%\setbeforesecskip{\onelineskip}
%\setbeforesecskip{18pt}
%\setaftersecskip{\onelineskip}
%
%% subsection
%\setbeforesubsecskip{\onelineskip}
%\setaftersubsecskip{\onelineskip}
%
%% subsubsection
%\setbeforesubsubsecskip{\onelineskip}
%\setaftersubsubsecskip{\onelineskip}
%
%% subsubsubsection
%\setbeforeparaskip{\onelineskip}
%\setafterparaskip{\onelineskip}   
% espaçamento entre um parágrafo e outro
%\setlength{\parskip}{0.2cm}


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% FONTES
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% redefinição de fontes
\renewcommand{\ABNTEXchapterfont}{\normalfont\bfseries}
\renewcommand{\ABNTEXchapterfontsize}{\normalsize} %{\Large}

\renewcommand{\ABNTEXpartfont}{\normalfont}
\renewcommand{\ABNTEXpartfontsize}{\ABNTEXchapterfontsize}

\renewcommand{\ABNTEXsectionfont}{\normalfont\bfseries}
\renewcommand{\ABNTEXsectionfontsize}{\normalsize} %{\Large}

\renewcommand{\ABNTEXsubsectionfont}{\normalfont}
\renewcommand{\ABNTEXsubsectionfontsize}{\normalsize} %{\large}

\renewcommand{\ABNTEXsubsubsectionfont}{\normalfont}
\renewcommand{\ABNTEXsubsubsectionfontsize}{\normalsize} %{\normalsize}

\renewcommand{\ABNTEXsubsubsubsectionfont}{\normalfont}
\renewcommand{\ABNTEXsubsubsubsectionfontsize}{\normalsize} %{\normalsize}


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% SUMÁRIO
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% travessão no sumário para apêndices e anexos
%\renewcommand{\cftsecindent}{0cm}


% insere espaço entre os itens do sumario de diferentes capítulos
% Modifica o espaçamento no sumário
% Não há espaços
\setlength{\cftbeforeparagraphskip}{0pt}
\setlength{\cftbeforesubsectionskip}{0pt}
\setlength{\cftbeforesectionskip}{0pt}
\setlength{\cftbeforesubsubsectionskip}{0pt}
\setlength{\cftbeforechapterskip}{0pt}

\renewcommand\cftchapterfont{\normalsize}
\renewcommand\cftsectionfont{\normalsize}
\renewcommand\cftsubsectionfont{\normalsize\normalfont}
\renewcommand\cftsubsubsectionfont{\normalsize\normalfont}


% Altera a fonte da seção quinária
\renewcommand*{\cftparagraphfont}{\normalfont\normalsize\itshape}

% Páginas do sumário não podem ser em negrito.
%\renewcommand\cftchapterpagefont{\normalfont}
\renewcommand\cftsectionpagefont{\normalfont}
\renewcommand\cftsubsectionpagefont{\normalfont}

% Altera a fonte da seção quinária
\renewcommand\cftparagraphpagefont{\normalfont}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% LISTAS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% define os títulos das listas
\addto\captionsbrazil{
	% ajusta nomes padrões do babel
	\renewcommand{\listadesiglasname}{Lista de abreviaturas e siglas}
	\renewcommand{\listadesimbolosname}{Lista de s\'imbolos}
	\renewcommand{\listfigurename}{Lista de figuras}
	\renewcommand{\listtablename}{Lista de tabelas}
	%\renewcommand{\listofquadrosname}{Lista de quadros}
	% ajusta nomes usados com a macro \autoref
	\renewcommand{\pageautorefname}{p\'agina}
	\renewcommand{\sectionautorefname}{Se{\c c}\~ao}
	\renewcommand{\subsectionautorefname}{Subse{\c c}\~ao}
	\renewcommand{\subsubsectionautorefname}{Subse{\c c}\~ao}
	\renewcommand{\paragraphautorefname}{Subse{\c c}\~ao}
}


\newcommand{\listofquadrosname}{ } 

% cria a lista de quadros
\newcommand{\quadroname}{Quadro}
\newfloat[chapter]{quadro}{loq}{\quadroname}
\newlistof{listofquadros}{loq}{\listofquadrosname}
\newlistentry{quadro}{loq}{0}

\counterwithout{quadro}{chapter}
\renewcommand{\cftquadroname}{\quadroname\space}
\renewcommand*{\cftquadroaftersnum}{\hfill--\hfill}



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CAPA
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\makeatletter
\renewcommand{\imprimircapa}{

	\begin{capa}

	\begin{figure}
	   \centering
	   		\includegraphics[scale=0.40]{04-figuras/brasaouesc.jpg}
    \end{figure}
		\quad
		\hspace{-1.5cm}
		\begin{minipage}{.95\textwidth}
			\begin{center}
			\normalfont\scshape\textbf{\imprimirinstituicao}\\\vspace*{0.3cm}
			\normalfont\scshape\textbf{\imprimirprograma}\\
			\abntex@ifnotempty\textbf{\imprimirareaconcentracao}
			{
				\normalfont\scshape{\imprimirareaconcentracao}
			}
			\end{center}
		\end{minipage}
		
	  \vspace*{60pt}
	
	\begin{center}
				\normalfont\scshape\textbf\imprimirautor
			\end{center}
			
		\vspace*{60pt}

		\begin{center}
			\ABNTEXchapterfont\scshape\textbf\imprimirtitulo
			\abntex@ifnotempty{\imprimirsubtitulo}{
				{\ABNTEXchapterfont\scshape\textbf{\hspace*{-0.3em}: }}{\ABNTEXchapterfont\large\scshape\imprimirsubtitulo}
			}
		\end{center}

		%\vspace*{20pt}

%		\begin{center}
%			\small\imprimirorientadorRotulo{} \imprimirorientador \\
%			\small\imprimirinstOrientador \\
%			\abntex@ifnotempty{\imprimircoorientador}
%			{
%				\begin{SingleSpacing}\par\end{SingleSpacing}
%				\small\imprimircoorientadorRotulo{} \imprimircoorientador \\
%				\small\imprimirinstCoorientador
%			}
%		\end{center}
%
		\vspace*{\fill}

		\begin{center}
			\normalfont\scshape\textbf{\imprimirlocal}\\
			\normalfont\scshape\textbf{\imprimirdata}
		\end{center}

	\end{capa}
}
\makeatother


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% FOLHA DE ROSTO
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\makeatletter
\renewcommand{\folhaderostocontent}{
	\setcounter{page}{2}
	\begin{center}
		{\normalfont\scshape\textbf\imprimirautor}
	\end{center}

	\vspace*{216pt}

	\begin{center}
		\ABNTEXchapterfont\scshape\textbf\imprimirtitulo
		\abntex@ifnotempty{\imprimirsubtitulo}{
			{\ABNTEXchapterfont\Large\scshape{\hspace*{-0.3em}: }}{\ABNTEXchapterfont\large\scshape\imprimirsubtitulo}
		}
	\end{center}

	\vspace*{36pt}

	\abntex@ifnotempty{\imprimirpreambulo}{
		\SingleSpacing
		\begin{tabular}{p{.37\textwidth}p{.13\textwidth}p{.50\textwidth}}
			& \multicolumn{2}{p{.50\textwidth}}{\normalfont\hyphenpenalty=10000{\imprimirpreambulo}} \\ & & \\
			\abntex@ifnotempty{\imprimirareaconcentracao}
			{
				& \multicolumn{2}{p{.5\textwidth}}{\normalfont\hyphenpenalty=10000{\imprimirareaconcentracaoRotulo\imprimirareaconcentracao}} \\ & & \\
			}
			\abntex@ifnotempty{\imprimirlinhapesquisa}
			{
					& \multicolumn{2}{p{.5\textwidth}}{\normalfont\hyphenpenalty=10000{\imprimirlinhapesquisaRotulo\imprimirlinhapesquisa}} \\ & & \\
			}
			
			\abntex@ifnotempty{\imprimirorientador}
			{
					& \multicolumn{2}{p{.5\textwidth}}{\normalfont\hyphenpenalty=10000{\imprimirorientadorRotulo\imprimirorientador}}  \\
			}
			
		
			
			\abntex@ifnotempty{\imprimircoorientador}
			{
				& \multicolumn{2}{p{.5\textwidth}}{\normalfont\hyphenpenalty=10000{\imprimircoorientadorRotulo\imprimircoorientador}} \\ & & \\
				
			}
		\end{tabular}
	}

	\vspace*{\fill}

	\begin{center}
	%	\normalfont\scshape{\imprimirinstituicao}\\
	%	\normalfont\scshape{\imprimirprograma}\\
		\ABNTEXchapterfont\scshape\textbf{\imprimirlocal}\\
		\ABNTEXchapterfont\scshape\textbf{\imprimirdata}
	\end{center}
}
\makeatother

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% DEDICATORIA
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\renewenvironment{dedicatoria}[1][]
{
	\ifthenelse{\equal{#1}{}}{
		\PRIVATEbookmarkthis{\dedicatorianame}
	}{\pretextualchapter{#1}}

	\vspace*{\fill}

	\begin{flushright}
		\begin{minipage}{.5\textwidth}
			\begin{SingleSpacing}
				\setlength\parindent{0pt}
				\setlength\parskip{12pt}
}
{
			\end{SingleSpacing}
		\end{minipage}
	\end{flushright}
}


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EPIGRAFE
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\renewenvironment{epigrafe}[1][]
{
	\ifthenelse{\equal{#1}{}}{
		\PRIVATEbookmarkthis{\epigraphname}
	}{\pretextualchapter{#1}}

	\vspace*{\fill}

	\begin{flushright}
		\begin{minipage}{.5\textwidth}
			\begin{SingleSpacing}
				\setlength\parindent{0pt}
				\setlength\parskip{12pt}
}
{
			\end{SingleSpacing}
		\end{minipage}
	\end{flushright}
}
