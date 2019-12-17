from pyadjoint.tape import annotate_tape, stop_annotating, get_working_tape
from pyadjoint.overloaded_type import create_overloaded_object

def annotate_project(project):

    def wrapper(*args, **kwargs):
        """The project call performs an equation solve, and so it too must be annotated so that the
        adjoint and tangent linear models may be constructed automatically by pyadjoint.

        To disable the annotation of this function, just pass :py:data:`annotate=False`. This is useful in
        cases where the solve is known to be irrelevant or diagnostic for the purposes of the adjoint
        computation (such as projecting fields to other function spaces for the purposes of
        visualisation)."""

        annotate = annotate_tape(kwargs)
        with stop_annotating():
            output = project(*args, **kwargs)
        output = create_overloaded_object(output)

        if annotate:
            from fenics_adjoint.solving import SolveBlock
            from fenics_adjoint.projection import ProjectBlock
            bcs = kwargs.pop("bcs", [])
            sb_kwargs = SolveBlock.pop_kwargs(kwargs)
            block = ProjectBlock(args[0], args[1], output, bcs, **sb_kwargs)

            tape = get_working_tape()
            tape.add_block(block)

            block.add_output(output.block_variable)

        return output

    return wrapper
