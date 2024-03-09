# VRP VNS Open Routes
VRP-VNS-Open-Routes is a solution to the Vehicle Routing Problem (VRP) especially created for optimizing tonkilometer-related logistics for Open Routes Problems. This project represents a fusion of powerful VRP algorithms, Variable Neighborhood Search (VNS), and Local Search operators such as Two-Opt, Swaps, and Relocations. Blending heuristics and metaheuristics, our solution tackles logistics planning with efficiency at its core, minimizing the overall energy required for product transportation (by minimizing tonkilometers based on distances between spots and cargo carried -plus vehicles' deadweight- during every kilometer), consequently reducing transportation costs.

It is essential to highlight that the solution generated is not optimal due to the impractical execution time associated with an exhaustive approach. However, by leveraging heuristics and metaheuristics, our program efficiently discovers a highly effective solution within a reasonable timeframe. This strategic combination of algorithms ensures a swift and practical resolution to the problem, striking a balance between solution quality and computational efficiency.

## The operational scenario is outlined as follows:

### Delivery Setup :
Transportation of products from a central warehouse to 250 customers (N = {1,2, … ,250}) located at various locations.
Each customer i ∈ N has ordered a quantity of products denoted as 𝑑ᵢ. ***All this data can be found in file Instance.txt which is read by the program***.

### Fleet and Vehicle Specifications:
Utilization of a homogeneous fleet of vehicles with an empty weight 𝛚 = 6 tn and a maximum transportable load 𝑄 = 8 tn.
Each truck initiates its route from the central warehouse 𝑑 = {0} and sequentially visits a set of customers.

### Routing Constraints:
Each customer i ∈ N is served by a single vehicle in a single visit, with the delivery of the required products 𝑑ᵢ.

### Completion of Routes:
Routes are completed at the last customer served, implying an open route scenario.

### Cost Calculation:
The cost of the entire transportation activity is computed based on the total ton-kilometers (tn x km) covered by the routes.

### Optimization Objectives:
The design of routes aims to minimize the total mixed ton-kilometers, considering both the truck's deadweight and the weight of the transported cargo.

### Algorithmic Approach:
* Integration of VRP Algorithm especially designed for Open Routes and ton - kilometers. 
* Variable Neighborhood Search (VNS) for dynamic exploration of solution spaces after the initial solution creation.
  * Incorporation of Local Search operators, including Two-Opt, Swaps and Relocations.

## Excecution of the program
To run the program, use the command `python main.py`. An ***output.txt*** will be created containing the ***problem's solution (total tonkilometers and the routes in the solution produced)***. In this repository you can find the output.txt created for the specifications provided in the Instance.txt. By using the command `python sol_checker.py` you can test if the solution in the output.txt generated is correct. 

## Team of developers
| Full Name | Github Account |
| --- | --- |
| Kapetanaki Elina | [ElinaKapetanaki](https://github.com/ElinaKapetanaki) |
| Kirikos Aggelos | [aggekirikos](https://github.com/aggekirikos) | 
| Siamantouras Vaggelis | [evansiam](https://github.com/evansiam) | 
| Tsagkaraki Aggeliki | [Angeliki03](https://github.com/Angeliki03) | 
| Tsetsila Despoina | [DespoinaTsetsila](https://github.com/DespoinaTsetsila) |
| Chlouveraki Nikol | [nikochlouveraki](https://github.com/nikochlouveraki) |