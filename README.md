# Checking graph minors

This is a simple python script that checks if a given graph contains a $k$-clique as a minor. It works by encoding the problem in CNF form, which is then solved with [CaDiCal](https://github.com/arminbiere/cadical).

## Dependencies

The software uses [NetworkX](https://github.com/networkx/networkx) and [PySAT](https://github.com/pysathq/pysat), which can be installed with
```
 pip install networkx && pip install python-sat
```

## Usage
When using the command line, run the script with:
```
python MinorChecker.py <input graph> <k>
```
where <input graph> is a either a text file containing the graph in DIMACS format or a .pkl/.pickle object containing a networkx graph and k is an integer specifying the size of the clique minor to check.
Alternatively, when using the software as a module it can be used as follows
```
minor_checker = MinorChecker(graph,k) # where graph is an nx graph and k the size of the clique
minor_checker.run()
has_minor = minor_checker.contains_minor() # returns a boolean depending on if the graph contains a k minor
solution = minor_checker.get_solution() # outputs a list of size n, where the v-th index denotes the connected component vertex v belongs to. -1 denotes an unassigned vertex
runtime = minor_checker.get_runtime() gets the runtime of the algorithm
```
