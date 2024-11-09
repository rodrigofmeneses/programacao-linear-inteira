import pyomo.environ as pyo


def build_model():
    model = pyo.ConcreteModel()

    # Sets
    model.INSPETORES = pyo.Set(initialize=["I", "II"])

    # Parameters
    model.PecasInspecionadasMin = pyo.Param(initialize=1800)
    model.HorasExpediente = pyo.Param(initialize=8)
    model.TaxaDeInspecao = pyo.Param(model.INSPETORES, initialize={"I": 25, "II": 15})
    model.TaxaDeConfiabilidade = pyo.Param(
        model.INSPETORES, initialize={"I": 0.98, "II": 0.95}
    )
    model.CustoHora = pyo.Param(model.INSPETORES, initialize={"I": 4, "II": 3})
    model.CustoErro = pyo.Param(initialize=2)
    model.DisponibilidadeInspetores = pyo.Param(
        model.INSPETORES, initialize={"I": 8, "II": 10}
    )

    # Variables
    model.contratacao = pyo.Var(model.INSPETORES, domain=pyo.NonNegativeIntegers)

    # Constraints
    @model.Constraint()
    def atendimento_demandas(model):
        return (
            sum(
                model.contratacao[inspetor]
                * model.TaxaDeInspecao[inspetor]
                * model.TaxaDeConfiabilidade[inspetor]
                * model.HorasExpediente
                for inspetor in model.INSPETORES
            )
            >= model.PecasInspecionadasMin
        )

    @model.Constraint(model.INSPETORES)
    def disponibilidade_inspetores(model, inspetor):
        return model.contratacao[inspetor] <= model.DisponibilidadeInspetores[inspetor]

    # Objective Function
    def objective_function(model):
        return sum(
            model.contratacao[inspetor] * model.CustoHora[inspetor]
            for inspetor in model.INSPETORES
        ) + sum(
            model.contratacao[inspetor]
            * model.TaxaDeInspecao[inspetor]
            * model.TaxaDeConfiabilidade[inspetor]
            * model.CustoErro
            for inspetor in model.INSPETORES
        )

    model.objective = pyo.Objective(rule=objective_function, sense=pyo.minimize)

    return model


if __name__ == "__main__":
    model = build_model()
    solver = pyo.SolverFactory("cbc")
    solver.solve(model)

    for inspetor in model.INSPETORES:
        print(
            f"Contratação de inspetor {inspetor}: {model.contratacao[inspetor].value}"
        )
