from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Disciplina:
    nome: str
    codigo: str
    creditos: int
    vagas_totais: int
    vagas_ocupadas: int = 0
    pre_requisitos: List[str] = field(default_factory=list)

    def tem_vagas(self) -> bool:
        return self.vagas_ocupadas < self.vagas_totais


@dataclass
class Aluno:
    nome: str
    matricula: str
    disciplinas_concluidas: List[str] = field(default_factory=list)
    disciplinas_matriculadas: List[Disciplina] = field(default_factory=list)

    def creditos_matriculados(self) -> int:
        return sum(d.creditos for d in self.disciplinas_matriculadas)


class SistemaGestaoAcademica:
    LIMITE_CREDITOS_POR_SEMESTRE = 24

    def __init__(self):
        self.matriculas_realizadas: List[tuple] = []

    def realizar_matricula(self, aluno: Aluno,
                            disciplinas_desejadas: List[Disciplina]) -> List[Disciplina]:
        print(f"\n[1] {aluno.nome} acessa o sistema.")
        print(f"[2] Aluno escolhe disciplinas: "
              f"{[d.nome for d in disciplinas_desejadas]}.")

        matriculadas_com_sucesso: List[Disciplina] = []

        for disciplina in disciplinas_desejadas:
            print(f"\n  -> Processando disciplina: {disciplina.nome}")

            faltantes = [pr for pr in disciplina.pre_requisitos
                         if pr not in aluno.disciplinas_concluidas]
            if faltantes:
                print(f"  [3A] Pré-requisito(s) não atendido(s): {faltantes}. "
                      f"Matrícula em '{disciplina.nome}' negada.")
                continue
            print("  [3] Pré-requisitos atendidos.")

            if not disciplina.tem_vagas():
                print(f"  [4A] Turma lotada para '{disciplina.nome}'. Matrícula negada.")
                continue
            print("  [4] Vagas disponíveis.")

            creditos_projetados = aluno.creditos_matriculados() + disciplina.creditos
            if creditos_projetados > self.LIMITE_CREDITOS_POR_SEMESTRE:
                print(f"  [!] Limite de {self.LIMITE_CREDITOS_POR_SEMESTRE} créditos "
                      f"por semestre seria excedido ({creditos_projetados}). "
                      f"Matrícula em '{disciplina.nome}' negada.")
                continue

            disciplina.vagas_ocupadas += 1
            aluno.disciplinas_matriculadas.append(disciplina)
            self.matriculas_realizadas.append((aluno, disciplina))
            matriculadas_com_sucesso.append(disciplina)
            print(f"  [5] Matrícula em '{disciplina.nome}' confirmada.")

        print(f"\nResumo: {aluno.nome} matriculado em "
              f"{[d.nome for d in matriculadas_com_sucesso]} "
              f"(total {aluno.creditos_matriculados()} créditos).")

        return matriculadas_com_sucesso


def escolher_multiplos_da_lista(itens: Dict[str, Disciplina]) -> List[Disciplina]:
    if not itens:
        print("Nenhuma disciplina cadastrada ainda.")
        return []
    chaves = list(itens.keys())
    for i, chave in enumerate(chaves, start=1):
        d = itens[chave]
        print(f"  {i}. {d.nome} ({d.codigo}) - {d.creditos} créditos")
    escolha = input("Digite os números das disciplinas separados por vírgula: ").strip()
    selecionadas = []
    for parte in escolha.split(","):
        parte = parte.strip()
        if parte.isdigit() and 1 <= int(parte) <= len(chaves):
            selecionadas.append(itens[chaves[int(parte) - 1]])
    return selecionadas


def escolher_da_lista(itens: Dict[str, object], rotulo: str):
    if not itens:
        print(f"Nenhum(a) {rotulo} cadastrado(a) ainda.")
        return None
    chaves = list(itens.keys())
    for i, chave in enumerate(chaves, start=1):
        print(f"  {i}. {chave}")
    escolha = input(f"Escolha o número do(a) {rotulo}: ").strip()
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(chaves)):
        print("Escolha inválida.")
        return None
    return itens[chaves[int(escolha) - 1]]


def cadastrar_disciplina(disciplinas: Dict[str, Disciplina]):
    nome = input("Nome da disciplina: ").strip()
    codigo = input("Código da disciplina: ").strip()
    try:
        creditos = int(input("Quantidade de créditos: "))
    except ValueError:
        creditos = 0
    try:
        vagas = int(input("Quantidade de vagas: "))
    except ValueError:
        vagas = 0
    pre_req_texto = input("Códigos de pré-requisitos separados por vírgula (Enter se nenhum): ").strip()
    pre_requisitos = [p.strip() for p in pre_req_texto.split(",") if p.strip()]
    disciplinas[codigo] = Disciplina(nome=nome, codigo=codigo, creditos=creditos,
                                      vagas_totais=vagas, pre_requisitos=pre_requisitos)
    print(f"Disciplina '{nome}' cadastrada.")


def cadastrar_aluno(alunos: Dict[str, Aluno]):
    nome = input("Nome do aluno: ").strip()
    matricula = input("Matrícula: ").strip()
    concluidas_texto = input("Códigos de disciplinas já concluídas, separados por vírgula (Enter se nenhuma): ").strip()
    concluidas = [c.strip() for c in concluidas_texto.split(",") if c.strip()]
    alunos[matricula] = Aluno(nome=nome, matricula=matricula, disciplinas_concluidas=concluidas)
    print(f"Aluno '{nome}' cadastrado.")


def realizar_matricula_interativo(sistema: SistemaGestaoAcademica,
                                   alunos: Dict[str, Aluno],
                                   disciplinas: Dict[str, Disciplina]):
    print("\nSelecione o aluno:")
    aluno = escolher_da_lista(alunos, "aluno")
    if aluno is None:
        return

    print("\nSelecione as disciplinas desejadas:")
    disciplinas_desejadas = escolher_multiplos_da_lista(disciplinas)
    if not disciplinas_desejadas:
        print("Nenhuma disciplina selecionada.")
        return

    sistema.realizar_matricula(aluno, disciplinas_desejadas)


def listar_disciplinas(disciplinas: Dict[str, Disciplina]):
    if not disciplinas:
        print("Nenhuma disciplina cadastrada.")
        return
    for d in disciplinas.values():
        print(f"- {d.nome} ({d.codigo}) - {d.creditos} créditos - "
              f"vagas {d.vagas_ocupadas}/{d.vagas_totais} - "
              f"pré-requisitos: {d.pre_requisitos or 'nenhum'}")


def menu():
    sistema = SistemaGestaoAcademica()
    alunos: Dict[str, Aluno] = {}
    disciplinas: Dict[str, Disciplina] = {}

    opcoes = {
        "1": ("Cadastrar disciplina", lambda: cadastrar_disciplina(disciplinas)),
        "2": ("Cadastrar aluno", lambda: cadastrar_aluno(alunos)),
        "3": ("Realizar matrícula", lambda: realizar_matricula_interativo(sistema, alunos, disciplinas)),
        "4": ("Listar disciplinas", lambda: listar_disciplinas(disciplinas)),
        "0": ("Sair", None),
    }

    while True:
        print("\n=== Sistema de Gestão Acadêmica ===")
        for chave, (texto, _) in opcoes.items():
            print(f"{chave}. {texto}")
        escolha = input("Escolha uma opção: ").strip()

        if escolha == "0":
            print("Encerrando.")
            break
        if escolha in opcoes:
            opcoes[escolha][1]()
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()
