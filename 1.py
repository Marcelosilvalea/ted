from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict


@dataclass
class Paciente:
    nome: str
    cpf: str
    consultas: List["Consulta"] = field(default_factory=list)

    def consultas_futuras(self) -> List["Consulta"]:
        agora = datetime.now()
        return [c for c in self.consultas if c.horario > agora and c.status == "confirmada"]


@dataclass
class Medico:
    nome: str
    especialidade: str
    agenda: List["Consulta"] = field(default_factory=list)

    def horario_ocupado(self, horario: datetime) -> bool:
        return any(c.horario == horario and c.status == "confirmada" for c in self.agenda)

    def horarios_disponiveis(self, opcoes: List[datetime]) -> List[datetime]:
        return [h for h in opcoes if not self.horario_ocupado(h)]


@dataclass
class Consulta:
    paciente: Paciente
    medico: Medico
    horario: datetime
    status: str = "pendente"


class SistemaAgendamento:
    MAX_CONSULTAS_FUTURAS = 3

    def __init__(self):
        self.consultas: List[Consulta] = []

    def solicitar_agendamento(self, paciente: Paciente, medico: Medico,
                               horarios_desejados: List[datetime]) -> Optional[Consulta]:
        print(f"\n[1] {paciente.nome} solicita agendamento com Dr(a). {medico.nome}.")

        if len(paciente.consultas_futuras()) >= self.MAX_CONSULTAS_FUTURAS:
            print(f"[!] {paciente.nome} já possui {self.MAX_CONSULTAS_FUTURAS} "
                  f"consultas futuras. Agendamento negado.")
            return None

        disponiveis = medico.horarios_disponiveis(horarios_desejados)
        print(f"[2] Horários disponíveis: {[h.strftime('%d/%m/%Y %H:%M') for h in disponiveis]}")

        if not disponiveis:
            print("[3A] Nenhum dos horários desejados está disponível. "
                  "Sistema sugere novos horários.")
            return None

        horario_escolhido = disponiveis[0]
        print(f"[3] Paciente escolhe o horário {horario_escolhido.strftime('%d/%m/%Y %H:%M')}.")

        if medico.horario_ocupado(horario_escolhido):
            print("[5A] Conflito de agenda detectado. Operação cancelada.")
            return None
        print("[4] Disponibilidade confirmada.")

        consulta = Consulta(paciente=paciente, medico=medico,
                             horario=horario_escolhido, status="confirmada")
        self.consultas.append(consulta)
        paciente.consultas.append(consulta)
        medico.agenda.append(consulta)
        print("[5] Consulta registrada.")

        print(f"[6] Confirmação enviada a {paciente.nome}: consulta com "
              f"Dr(a). {medico.nome} em {horario_escolhido.strftime('%d/%m/%Y %H:%M')}.")

        return consulta


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


def cadastrar_paciente(pacientes: Dict[str, Paciente]):
    nome = input("Nome do paciente: ").strip()
    cpf = input("CPF do paciente: ").strip()
    pacientes[cpf] = Paciente(nome=nome, cpf=cpf)
    print(f"Paciente '{nome}' cadastrado.")


def cadastrar_medico(medicos: Dict[str, Medico]):
    nome = input("Nome do médico: ").strip()
    especialidade = input("Especialidade: ").strip()
    medicos[nome] = Medico(nome=nome, especialidade=especialidade)
    print(f"Médico '{nome}' cadastrado.")


def solicitar_agendamento_interativo(sistema: SistemaAgendamento,
                                      pacientes: Dict[str, Paciente],
                                      medicos: Dict[str, Medico]):
    print("\nSelecione o paciente:")
    paciente = escolher_da_lista({p.cpf: p for p in pacientes.values()}, "paciente")
    if paciente is None:
        return

    print("\nSelecione o médico:")
    medico = escolher_da_lista(medicos, "médico")
    if medico is None:
        return

    horarios = []
    try:
        qtd = int(input("Quantos horários deseja informar? "))
    except ValueError:
        print("Valor inválido.")
        return

    for i in range(qtd):
        texto = input(f"Horário {i + 1} (dd/mm/aaaa hh:mm): ").strip()
        try:
            horarios.append(datetime.strptime(texto, "%d/%m/%Y %H:%M"))
        except ValueError:
            print("Formato inválido, horário ignorado.")

    if not horarios:
        print("Nenhum horário válido informado.")
        return

    sistema.solicitar_agendamento(paciente, medico, horarios)


def listar_consultas(sistema: SistemaAgendamento):
    if not sistema.consultas:
        print("Nenhuma consulta registrada.")
        return
    for c in sistema.consultas:
        print(f"- {c.paciente.nome} com Dr(a). {c.medico.nome} em "
              f"{c.horario.strftime('%d/%m/%Y %H:%M')} [{c.status}]")


def menu():
    sistema = SistemaAgendamento()
    pacientes: Dict[str, Paciente] = {}
    medicos: Dict[str, Medico] = {}

    opcoes = {
        "1": ("Cadastrar paciente", lambda: cadastrar_paciente(pacientes)),
        "2": ("Cadastrar médico", lambda: cadastrar_medico(medicos)),
        "3": ("Solicitar agendamento", lambda: solicitar_agendamento_interativo(sistema, pacientes, medicos)),
        "4": ("Listar consultas", lambda: listar_consultas(sistema)),
        "0": ("Sair", None),
    }

    while True:
        print("\n=== Sistema de Agendamento de Consultas Médicas ===")
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
