# SymmetryGroupPuzzle

A game based on overlapping symmetry groups.

My first implementation (version 1) suffered from speed issues, and was
limited in the topologies of the cut-shapes.  My second implementation,
however, should overcome these problems.  Unfortunately, it's come with
its own set of problems, and they should have been predictable.  (Intuitively,
I think I did sense the problem before I started, but thought maybe it wouldn't
be so bad.)  The main problem is that a rectangular grid of pixels can't cleanly
undergo a non-rectangular automorphism.  Consequently, the artifacting compounds
itself as permutations are concatinated over and over.  This second implementation
(version 2), in order to solve the artifacting problem, must be limited to axis-
aligned shapes that only make right-angle turns.  Yes, we can do arbitrary topologies,
but the shapes can't have edges that are diagonal in any way.  And even still, we
would need to very carefully generate the permutations (automorphisms of the shape)
to prevent artifacting.