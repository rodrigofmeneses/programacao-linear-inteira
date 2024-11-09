import pyomo.environ as pyo


def build_model():
    """
    Modela para o problema de planejamento de produção e distribuição das fábricas para revenda.
    """
    model = pyo.ConcreteModel()

    # Sets
    model.FABRICAS = pyo.Set(initialize=["São Paulo", "João Pessoa", "Manaus"])
    model.REVENDAS = pyo.Set(
        initialize=["Rio de Janeiro", "Salvador", "Aracaju", "Maceió", "Recife"]
    )

    # Parameters
    model.Demanda = pyo.Param(
        model.REVENDAS,
        initialize={
            "Rio de Janeiro": 6000,
            "Salvador": 5000,
            "Aracaju": 2000,
            "Maceió": 1000,
            "Recife": 3000,
        },
    )

    model.ProducaoMaxima = pyo.Param(
        model.FABRICAS,
        initialize={"São Paulo": 10000, "João Pessoa": 5000, "Manaus": 6000},
    )

    model.CustoTransporte = pyo.Param(
        model.FABRICAS,
        model.REVENDAS,
        initialize={
            ("São Paulo", "Rio de Janeiro"): 1000,
            ("São Paulo", "Salvador"): 2000,
            ("São Paulo", "Aracaju"): 3000,
            ("São Paulo", "Maceió"): 3500,
            ("São Paulo", "Recife"): 4000,
            ("João Pessoa", "Rio de Janeiro"): 4000,
            ("João Pessoa", "Salvador"): 2000,
            ("João Pessoa", "Aracaju"): 1500,
            ("João Pessoa", "Maceió"): 1200,
            ("João Pessoa", "Recife"): 1000,
            ("Manaus", "Rio de Janeiro"): 6000,
            ("Manaus", "Salvador"): 4000,
            ("Manaus", "Aracaju"): 3500,
            ("Manaus", "Maceió"): 3000,
            ("Manaus", "Recife"): 2000,
        },
    )

    # Variables
    model.x = pyo.Var(model.FABRICAS, model.REVENDAS, domain=pyo.NonNegativeIntegers)

    # Constraints
    @model.Constraint(model.REVENDAS)
    def atendimento_demandas(model, revenda):
        return (
            sum(model.x[fabrica, revenda] for fabrica in model.FABRICAS)
            == model.Demanda[revenda]
        )

    @model.Constraint(model.FABRICAS)
    def capacidade_fabricas(model, fabrica):
        return (
            sum(model.x[fabrica, revenda] for revenda in model.REVENDAS)
            <= model.ProducaoMaxima[fabrica]
        )

    # Objetivo
    def funcao_objetivo(model):
        return sum(
            model.CustoTransporte[fabrica, revenda] * model.x[fabrica, revenda]
            for fabrica in model.FABRICAS
            for revenda in model.REVENDAS
        )

    model.objetivo = pyo.Objective(rule=funcao_objetivo, sense=pyo.minimize)

    return model

if __name__ == "__main__":
    model = build_model()
    solver = pyo.SolverFactory("cbc")
    solver.solve(model)

    print("Custo total: ", pyo.value(model.objetivo))

    for fabrica in model.FABRICAS:
        for revenda in model.REVENDAS:
            if pyo.value(model.x[fabrica, revenda]) > 0:
                print(
                    "De {} para {}: {}".format(
                        fabrica, revenda, pyo.value(model.x[fabrica, revenda])
                    )
                )