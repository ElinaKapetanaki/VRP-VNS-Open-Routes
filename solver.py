from VRP_Model import *


class Solution:
    def __init__(self):
        self.cost = 0.0
        self.routes = []


class RelocationMove(object):
    def __init__(self):
        self.originRoutePosition = None
        self.targetRoutePosition = None
        self.originNodePosition = None
        self.targetNodePosition = None
        self.costChangeOriginRt = None
        self.costChangeTargetRt = None
        self.moveCost = None

    def Initialize(self):
        self.originRoutePosition = None
        self.targetRoutePosition = None
        self.originNodePosition = None
        self.targetNodePosition = None
        self.costChangeOriginRt = None
        self.costChangeTargetRt = None
        self.moveCost = 10 ** 9


class SwapMove(object):
    def __init__(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = None

    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = 10 ** 9


class TwoOptMove(object):
    def __init__(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.moveCost = None

    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.moveCost = 10 ** 9


class CustomerInsertion(object):
    def __init__(self):
        # Customer to be inserted
        self.customer = None
        # Route where the insertion occurs
        self.route = None
        # Cost of the insertion
        self.cost = 10 ** 9


class Solver:

    def __init__(self, m):
        self.allNodes = m.allNodes
        self.customers = m.customers
        self.depot = m.allNodes[0]
        self.distanceMatrix = m.matrix
        self.capacity = m.capacity
        self.sol = None
        self.bestSolution = None

    def solve(self):
        self.SetRoutedFlagToFalseForAllCustomers()
        self.sol = Solution()
        self.ApplyNearestNeighborMethod()
        self.LocalSearch(2)
        self.VND()
        return self.sol

    def SetRoutedFlagToFalseForAllCustomers(self):
        for i in range(0, len(self.customers)):
            self.customers[i].isRouted = False

    def ApplyNearestNeighborMethod(self):
        modelIsFeasible = True
        insertions = 0
        while insertions < len(self.customers):
            bestInsertion = CustomerInsertion()
            lastOpenRoute: Route = self.GetLastOpenRoute()
            if lastOpenRoute is not None:
               self.IdentifyBestInsertion(bestInsertion, lastOpenRoute)
            if bestInsertion.customer is not None:
                # Apply the best customer insertion
                self.ApplyCustomerInsertion(bestInsertion)
                insertions += 1
            else:
                # If there is an empty available route
                if lastOpenRoute is not None and len(lastOpenRoute.sequenceOfNodes) == 2:
                    modelIsFeasible = False
                    break
                else:
                    rt = Route(self.depot, self.capacity)
                    self.sol.routes.append(rt)
        
        if (modelIsFeasible == False):
            print('FeasibilityIssue')

    def GetLastOpenRoute(self):
        # Return the last open route in the current solution
        if len(self.sol.routes) == 0:
            return None
        else:
            return self.sol.routes[-1]

    def IdentifyBestInsertion(self, bestInsertion, rt):
        # Identify the best insertion point for an unrouted customer in a given route

        for i in range(0, len(self.customers)):

            candidateCust: Node = self.customers[i]
            if candidateCust.isRouted is False:
                # Check if adding the customer to the route violates its capacity constraint
                if rt.load + candidateCust.demand <= rt.capacity:
                    lastNodePresentInTheRoute = rt.sequenceOfNodes[-2]
                    # Calculate the cost of inserting the customer at various positions in the route
                    cumulativeCost = 0
                    for y in range(0, len(rt.sequenceOfNodes)-1):
                        from_n = rt.sequenceOfNodes[y]
                        to_n = rt.sequenceOfNodes[y+1]
                        cumulativeCost += candidateCust.demand * self.distanceMatrix[from_n.ID][to_n.ID]
                    trialCost = self.distanceMatrix[lastNodePresentInTheRoute.ID][candidateCust.ID] * (candidateCust.demand + 6)
                    trialCost += cumulativeCost

                    if trialCost < bestInsertion.cost:
                        # Update the bestInsertion object with details of the best insertion found
                        bestInsertion.customer = candidateCust
                        bestInsertion.route = rt
                        bestInsertion.cost = trialCost

    def ApplyCustomerInsertion(self, insertion):
        insCustomer = insertion.customer
        rt = insertion.route
        # before the second depot occurrence
        insIndex = len(rt.sequenceOfNodes) - 1
        rt.sequenceOfNodes.insert(insIndex, insCustomer)

        costAdded = insertion.cost

        rt.cost += costAdded
        self.sol.cost += costAdded

        rt.load += insCustomer.demand

        insCustomer.isRouted = True

    def VND(self):
        self.bestSolution = self.cloneSolution(self.sol)
        VNDIterator = 0
        kmax = 2
        rm = RelocationMove()
        sm = SwapMove()
        top = TwoOptMove()
        k = 0

        while k <= kmax:
            self.InitializeOperators(rm, sm, top)
            if k == 2:
                self.FindBestRelocationMove(rm)
                if rm.originRoutePosition is not None and rm.moveCost < 0:
                    self.ApplyRelocationMove(rm)

                    VNDIterator = VNDIterator + 1

                    k = 0
                else:
                    k += 1
            elif k == 1:
                self.FindBestSwapMove(sm)
                if sm.positionOfFirstRoute is not None and sm.moveCost < 0:
                    self.ApplySwapMove(sm)

                    VNDIterator = VNDIterator + 1

                    k = 0
                else:
                    k += 1
            elif k == 0:
                self.FindBestTwoOptMove(top)
                if top.positionOfFirstRoute is not None and top.moveCost < 0:
                    self.ApplyTwoOptMove(top)

                    VNDIterator = VNDIterator + 1

                    k = 0
                else:
                    k += 1

            if self.sol.cost < self.bestSolution.cost:
                self.bestSolution = self.cloneSolution(self.sol)

    def LocalSearch(self, operator):
        self.bestSolution = self.cloneSolution(self.sol)
        terminationCondition = False
        localSearchIterator = 0

        rm = RelocationMove()
        sm = SwapMove()
        top = TwoOptMove()

        while terminationCondition is False:

            self.InitializeOperators(rm, sm, top)

            # Relocations
            if operator == 0:
                self.FindBestRelocationMove(rm)
                if rm.originRoutePosition is not None:
                    if rm.moveCost < 0:
                        self.ApplyRelocationMove(rm)
                    else:
                        terminationCondition = True
            # Swaps
            elif operator == 1:
                self.FindBestSwapMove(sm)
                if sm.positionOfFirstRoute is not None:
                    if sm.moveCost < 0:
                        self.ApplySwapMove(sm)
                    else:
                        terminationCondition = True
            elif operator == 2:
                self.FindBestTwoOptMove(top)
                if top.positionOfFirstRoute is not None:
                    if top.moveCost < 0:
                        self.ApplyTwoOptMove(top)
                    else:
                        terminationCondition = True

            #self.TestSolution()

            if (self.sol.cost < self.bestSolution.cost):
                self.bestSolution = self.cloneSolution(self.sol)

            localSearchIterator = localSearchIterator + 1

        self.sol = self.bestSolution

    def InitializeOperators(self, rm, sm, top):
        rm.Initialize()
        sm.Initialize()
        top.Initialize()

    def cloneRoute(self, rt:Route):
        cloned = Route(self.depot, self.capacity)
        cloned.cost = rt.cost
        cloned.load = rt.load
        cloned.sequenceOfNodes = rt.sequenceOfNodes.copy()
        return cloned

    def cloneSolution(self, sol: Solution):
        cloned = Solution()
        for i in range (0, len(sol.routes)):
            rt = sol.routes[i]
            clonedRoute = self.cloneRoute(rt)
            cloned.routes.append(clonedRoute)
        cloned.cost = self.sol.cost
        return cloned

    def FindBestSwapMove(self, sm):
        for firstRouteIndex in range(0, len(self.sol.routes)):
            rt1: Route = self.sol.routes[firstRouteIndex]
            pr1 = rt1.cost
            for secondRouteIndex in range(firstRouteIndex, len(self.sol.routes)):
                rt2: Route = self.sol.routes[secondRouteIndex]
                pr2 = rt2.cost
                for firstNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):
                    startOfSecondNodeIndex = 1
                    if rt1 == rt2:
                        startOfSecondNodeIndex = firstNodeIndex + 1
                    for secondNodeIndex in range(startOfSecondNodeIndex, len(rt2.sequenceOfNodes) - 1):

                        b1 = rt1.sequenceOfNodes[firstNodeIndex]

                        b2 = rt2.sequenceOfNodes[secondNodeIndex]

                        if rt1 != rt2:
                            # Handle different-route swap
                            if rt1.load - b1.demand + b2.demand > self.capacity or \
                               rt2.load - b2.demand + b1.demand > self.capacity:
                                continue

                            rt1.sequenceOfNodes[firstNodeIndex] = b2
                            rt2.sequenceOfNodes[secondNodeIndex] = b1
                            cost1, d1 = self.calculate_route_details(rt1.sequenceOfNodes, 6)
                            cost2, d2 = self.calculate_route_details(rt2.sequenceOfNodes, 6)
                            rt1.sequenceOfNodes[firstNodeIndex] = b1
                            rt2.sequenceOfNodes[secondNodeIndex] = b2
                            costChangeFirstRoute = - pr1 + cost1
                            costChangeSecondRoute = - pr2 + cost2
                            moveCost = - pr1 - pr2 + cost1 + cost2
                        else:
                            rt1.sequenceOfNodes[firstNodeIndex] = b2
                            rt1.sequenceOfNodes[secondNodeIndex] = b1
                            cost1, d1 = self.calculate_route_details(rt1.sequenceOfNodes, 6)
                            rt1.sequenceOfNodes[firstNodeIndex] = b1
                            rt1.sequenceOfNodes[secondNodeIndex] = b2
                            moveCost = - pr1 + cost1
                            cost2 = cost1
                            costChangeFirstRoute = - pr1 + cost1
                            costChangeSecondRoute = - pr2 + cost2

                        if moveCost < sm.moveCost and abs(moveCost) > 0.0001:
                            self.StoreBestSwapMove(firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex, moveCost, costChangeFirstRoute, costChangeSecondRoute, sm)

        # Return the updated solution move
        return sm

    def StoreBestSwapMove(self, firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex, moveCost, costChangeFirstRoute, costChangeSecondRoute, sm):
        sm.positionOfFirstRoute = firstRouteIndex
        sm.positionOfSecondRoute = secondRouteIndex
        sm.positionOfFirstNode = firstNodeIndex
        sm.positionOfSecondNode = secondNodeIndex
        sm.costChangeFirstRt = costChangeFirstRoute
        sm.costChangeSecondRt = costChangeSecondRoute
        sm.moveCost = moveCost

    def ApplySwapMove(self, sm):
       rt1 = self.sol.routes[sm.positionOfFirstRoute]
       rt2 = self.sol.routes[sm.positionOfSecondRoute]
       b1 = rt1.sequenceOfNodes[sm.positionOfFirstNode]
       b2 = rt2.sequenceOfNodes[sm.positionOfSecondNode]
       rt1.sequenceOfNodes[sm.positionOfFirstNode] = b2
       rt2.sequenceOfNodes[sm.positionOfSecondNode] = b1

       if rt1 == rt2:
           rt1.cost += sm.moveCost
       else:
           rt1.cost += sm.costChangeFirstRt
           rt2.cost += sm.costChangeSecondRt

           rt1.load = rt1.load - b1.demand + b2.demand
           rt2.load = rt2.load + b1.demand - b2.demand

       self.sol.cost += sm.moveCost
       #self.TestSolution()

    def FindBestTwoOptMove(self, top, cost_of_segment_to_be=None):
        for rtInd1 in range(0, len(self.sol.routes)):
            rt1: Route = self.sol.routes[rtInd1]
            for rtInd2 in range(rtInd1, len(self.sol.routes)):
                rt2: Route = self.sol.routes[rtInd2]
                for nodeInd1 in range(0, len(rt1.sequenceOfNodes) - 1):
                    start2 = 0
                    if (rt1 == rt2):
                        start2 = nodeInd1 + 2

                    for nodeInd2 in range(start2, len(rt2.sequenceOfNodes) - 1):

                        A = rt1.sequenceOfNodes[nodeInd1]
                        B = rt1.sequenceOfNodes[nodeInd1 + 1]
                        K = rt2.sequenceOfNodes[nodeInd2]
                        L = rt2.sequenceOfNodes[nodeInd2 + 1]

                        if rt1 == rt2:
                            if nodeInd1 == 0 and nodeInd2 == len(rt1.sequenceOfNodes) - 2:
                                continue

                            reversedSegment = list(reversed(rt1.sequenceOfNodes[nodeInd1 + 1: nodeInd2 + 1]))
                            d_after_target_node_rt1 = sum(node.demand for node in rt1.sequenceOfNodes[nodeInd2 + 1:])

                            cost_cummulative_change_rt1 = 0
                            current_load = 6 + d_after_target_node_rt1 + B.demand
                            for i in range(len(reversedSegment) - 1, 0, -1):
                                pr = i - 1
                                n2 = reversedSegment[i]
                                n1 = reversedSegment[pr]
                                cost_cummulative_change_rt1 += current_load * self.distanceMatrix[n1.ID][n2.ID]
                                current_load += n1.demand

                            current_load = 6 + d_after_target_node_rt1 + K.demand
                            for i in range(nodeInd2, nodeInd1 + 1, -1):
                                pr = i - 1
                                n2 = rt1.sequenceOfNodes[i]
                                n1 = rt1.sequenceOfNodes[pr]
                                cost_cummulative_change_rt1 -= current_load * self.distanceMatrix[n1.ID][n2.ID]
                                current_load += n1.demand

                            d_after_origin_node_rt1 = sum(node.demand for node in reversedSegment) + d_after_target_node_rt1
                            cost_change_rt1 = 0

                            cost_change_rt1 += self.distanceMatrix[A.ID][K.ID] * (d_after_origin_node_rt1 + 6) + \
                                                self.distanceMatrix[B.ID][L.ID] * (d_after_target_node_rt1 + 6) - \
                                                self.distanceMatrix[A.ID][B.ID] * (d_after_origin_node_rt1 + 6) - \
                                                self.distanceMatrix[K.ID][L.ID] * (d_after_target_node_rt1 + 6)
                            originRtCostChange = cost_change_rt1 + cost_cummulative_change_rt1

                            moveCost = originRtCostChange
                        else:
                            if nodeInd1 == 0 and nodeInd2 == 0:
                                continue
                            if nodeInd1 == len(rt1.sequenceOfNodes) - 2 and nodeInd2 == len(rt2.sequenceOfNodes) - 2:
                                continue

                            if self.CapacityIsViolated(rt1, nodeInd1, rt2, nodeInd2):
                                continue

                            relocated_segment1 = rt1.sequenceOfNodes[nodeInd1 + 1:]
                            relocated_segment2 = rt2.sequenceOfNodes[nodeInd2 + 1:]
                            load_of_rt1s_segment = sum(node.demand for node in relocated_segment1) + 6
                            load_of_rt2s_segment = sum(node.demand for node in relocated_segment2) + 6

                            cost_cummulative_change_rt1 = 0
                            for i in range(0, nodeInd1):
                                next = i + 1
                                n1 = rt1.sequenceOfNodes[i]
                                n2 = rt1.sequenceOfNodes[next]
                                cost_cummulative_change_rt1 += load_of_rt2s_segment * self.distanceMatrix[n1.ID][n2.ID] - \
                                                                load_of_rt1s_segment * self.distanceMatrix[n1.ID][n2.ID]

                            cost_cummulative_change_rt2 = 0
                            for i in range(0, nodeInd2):
                                next = i + 1
                                n1 = rt2.sequenceOfNodes[i]
                                n2 = rt2.sequenceOfNodes[next]
                                cost_cummulative_change_rt2 += load_of_rt1s_segment * self.distanceMatrix[n1.ID][n2.ID] - \
                                                                load_of_rt2s_segment * self.distanceMatrix[n1.ID][n2.ID]

                            costAdded = self.distanceMatrix[A.ID][L.ID] * load_of_rt2s_segment + \
                                        self.distanceMatrix[K.ID][B.ID] * load_of_rt1s_segment
                            costRemoved = self.distanceMatrix[A.ID][B.ID] * load_of_rt1s_segment + \
                                            self.distanceMatrix[K.ID][L.ID] * load_of_rt2s_segment

                            moveCost = costAdded - costRemoved + \
                                        cost_cummulative_change_rt1 + cost_cummulative_change_rt2

                        if moveCost < top.moveCost and abs(moveCost) > 0.0001:
                            self.StoreBestTwoOptMove(rtInd1, rtInd2, nodeInd1, nodeInd2, moveCost, top)

    def CapacityIsViolated(self, rt1, nodeInd1, rt2, nodeInd2):

        rt1FirstSegmentLoad = 0
        for i in range(0, nodeInd1 + 1):
            n = rt1.sequenceOfNodes[i]
            rt1FirstSegmentLoad += n.demand
        rt1SecondSegmentLoad = rt1.load - rt1FirstSegmentLoad

        rt2FirstSegmentLoad = 0
        for i in range(0, nodeInd2 + 1):
            n = rt2.sequenceOfNodes[i]
            rt2FirstSegmentLoad += n.demand
        rt2SecondSegmentLoad = rt2.load - rt2FirstSegmentLoad

        if rt1FirstSegmentLoad + rt2SecondSegmentLoad > rt1.capacity:
            return True
        if rt2FirstSegmentLoad + rt1SecondSegmentLoad > rt2.capacity:
            return True

        return False

    def StoreBestTwoOptMove(self, rtInd1, rtInd2, nodeInd1, nodeInd2, moveCost, top):
        top.positionOfFirstRoute = rtInd1
        top.positionOfSecondRoute = rtInd2
        top.positionOfFirstNode = nodeInd1
        top.positionOfSecondNode = nodeInd2
        top.moveCost = moveCost

    def ApplyTwoOptMove(self, top):
        rt1: Route = self.sol.routes[top.positionOfFirstRoute]
        rt2: Route = self.sol.routes[top.positionOfSecondRoute]

        if rt1 == rt2:
            # reverses the nodes in the segment [positionOfFirstNode + 1,  top.positionOfSecondNode]
            reversedSegment = reversed(rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1])
            # lst = list(reversedSegment)
            # lst2 = list(reversedSegment)
            rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1] = reversedSegment

            # reversedSegmentList = list(reversed(rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1]))
            # rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1] = reversedSegmentList

            rt1.cost += top.moveCost

        else:
            # slice with the nodes from position top.positionOfFirstNode + 1 onwards
            relocatedSegmentOfRt1 = rt1.sequenceOfNodes[top.positionOfFirstNode + 1:]

            # slice with the nodes from position top.positionOfFirstNode + 1 onwards
            relocatedSegmentOfRt2 = rt2.sequenceOfNodes[top.positionOfSecondNode + 1:]

            del rt1.sequenceOfNodes[top.positionOfFirstNode + 1:]
            del rt2.sequenceOfNodes[top.positionOfSecondNode + 1:]

            rt1.sequenceOfNodes.extend(relocatedSegmentOfRt2)
            rt2.sequenceOfNodes.extend(relocatedSegmentOfRt1)

            self.UpdateRouteCostAndLoad(rt1)
            self.UpdateRouteCostAndLoad(rt2)

        self.sol.cost += top.moveCost
        #self.TestSolution()

    def UpdateRouteCostAndLoad(self, rt: Route):
        tot_dem = sum(n.demand for n in rt.sequenceOfNodes)
        rt.load = tot_dem
        tot_load = 6 + rt.load
        tn_km = 0
        for i in range(len(rt.sequenceOfNodes) - 1):
            from_node = rt.sequenceOfNodes[i]
            to_node = rt.sequenceOfNodes[i+1]
            tn_km += self.distanceMatrix[from_node.ID][to_node.ID] * tot_load
            tot_load -= to_node.demand
        rt.cost = tn_km

    def FindBestRelocationMove(self, rm):
        for originRouteIndex in range(0, len(self.sol.routes)):
            rt1: Route = self.sol.routes[originRouteIndex]
            for targetRouteIndex in range(0, len(self.sol.routes)):
                rt2: Route = self.sol.routes[targetRouteIndex]
                for originNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):
                    for targetNodeIndex in range(0, len(rt2.sequenceOfNodes) - 1):

                        if originRouteIndex == targetRouteIndex and (
                                targetNodeIndex == originNodeIndex or targetNodeIndex == originNodeIndex - 1):
                            continue

                        A = rt1.sequenceOfNodes[originNodeIndex - 1]
                        B = rt1.sequenceOfNodes[originNodeIndex]
                        C = rt1.sequenceOfNodes[originNodeIndex + 1]

                        F = rt2.sequenceOfNodes[targetNodeIndex]
                        G = rt2.sequenceOfNodes[targetNodeIndex + 1]

                        if rt1 != rt2:
                            if rt2.load + B.demand > rt2.capacity:
                                continue

                        d_after_origin_node_rt1 = sum(node.demand for node in rt1.sequenceOfNodes[originNodeIndex + 1:])
                        d_after_target_node_rt2 = sum(node.demand for node in rt2.sequenceOfNodes[targetNodeIndex + 1:])

                        if rt1 != rt2:

                            cost_cumulative_change_rt1 = 0
                            for i in range(0, originNodeIndex - 1):
                                next = i + 1
                                n1 = rt1.sequenceOfNodes[i]
                                n2 = rt1.sequenceOfNodes[next]
                                cost_cumulative_change_rt1 -= B.demand * self.distanceMatrix[n1.ID][n2.ID]
                            cost_change_rt1 = self.distanceMatrix[A.ID][C.ID] * (d_after_origin_node_rt1 + 6) - \
                                self.distanceMatrix[A.ID][B.ID] * (d_after_origin_node_rt1 + B.demand + 6) - \
                                self.distanceMatrix[B.ID][C.ID] * (d_after_origin_node_rt1 + 6)
                            originRtCostChange = cost_change_rt1 + cost_cumulative_change_rt1

                            cost_cummulative_change_rt2 = 0
                            for i in range(0, targetNodeIndex):
                                next = i + 1
                                n1 = rt2.sequenceOfNodes[i]
                                n2 = rt2.sequenceOfNodes[next]
                                cost_cummulative_change_rt2 += B.demand * self.distanceMatrix[n1.ID][n2.ID]

                            cost_change_rt2 = self.distanceMatrix[F.ID][B.ID] * (d_after_target_node_rt2 + B.demand + 6) + \
                                self.distanceMatrix[B.ID][G.ID] * (d_after_target_node_rt2 + 6) - \
                                self.distanceMatrix[F.ID][G.ID] * (d_after_target_node_rt2 + 6)
                            targetRtCostChange = cost_change_rt2 + cost_cummulative_change_rt2

                            moveCost = originRtCostChange + targetRtCostChange

                        else:

                            cost_cumulative_change_in_rt = 0

                            if originNodeIndex < targetNodeIndex:
                                for i in range(originNodeIndex + 1, targetNodeIndex):
                                    next = i + 1
                                    n1 = rt2.sequenceOfNodes[i]
                                    n2 = rt2.sequenceOfNodes[next]
                                    cost_cumulative_change_in_rt += B.demand * self.distanceMatrix[n1.ID][n2.ID]

                                cost_change_rt1 = self.distanceMatrix[A.ID][C.ID] * (d_after_origin_node_rt1 + B.demand + 6) - \
                                    self.distanceMatrix[A.ID][B.ID] * (d_after_origin_node_rt1 + B.demand + 6) - \
                                    self.distanceMatrix[B.ID][C.ID] * (d_after_origin_node_rt1 + 6) + \
                                    self.distanceMatrix[F.ID][B.ID] * (d_after_target_node_rt2 + B.demand + 6) + \
                                    self.distanceMatrix[B.ID][G.ID] * (d_after_target_node_rt2 + 6) - \
                                    self.distanceMatrix[F.ID][G.ID] * (d_after_target_node_rt2 + 6)
                            else:
                                for i in range(targetNodeIndex + 1, originNodeIndex - 1):
                                    next = i + 1
                                    n1 = rt2.sequenceOfNodes[i]
                                    n2 = rt2.sequenceOfNodes[next]
                                    cost_cumulative_change_in_rt -= B.demand * self.distanceMatrix[n1.ID][n2.ID]

                                cost_change_rt1 = self.distanceMatrix[A.ID][C.ID] * (d_after_origin_node_rt1 + 6) - \
                                    self.distanceMatrix[A.ID][B.ID] * (d_after_origin_node_rt1 + B.demand + 6) - \
                                    self.distanceMatrix[B.ID][C.ID] * (d_after_origin_node_rt1 + 6) + \
                                    self.distanceMatrix[F.ID][B.ID] * (d_after_target_node_rt2 + 6) + \
                                    self.distanceMatrix[B.ID][G.ID] * (d_after_target_node_rt2 - B.demand + 6) - \
                                    self.distanceMatrix[F.ID][G.ID] * (d_after_target_node_rt2 + 6)

                            moveCost = cost_change_rt1 + cost_cumulative_change_in_rt
                            originRtCostChange = moveCost
                            targetRtCostChange = moveCost

                        if (moveCost < rm.moveCost) and abs(moveCost) > 0.0001:
                            self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex,
                                                         targetNodeIndex, moveCost, originRtCostChange,
                                                         targetRtCostChange, rm)

        return rm.originRoutePosition

    def ApplyRelocationMove(self, rm: RelocationMove):

        originRt = self.sol.routes[rm.originRoutePosition]
        targetRt = self.sol.routes[rm.targetRoutePosition]

        B = originRt.sequenceOfNodes[rm.originNodePosition]

        if originRt == targetRt:
            del originRt.sequenceOfNodes[rm.originNodePosition]
            if rm.originNodePosition < rm.targetNodePosition:
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition, B)
            else:
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)

            originRt.cost += rm.moveCost

        else:
            del originRt.sequenceOfNodes[rm.originNodePosition]
            targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)
            originRt.cost += rm.costChangeOriginRt
            targetRt.cost += rm.costChangeTargetRt
            originRt.load -= B.demand
            targetRt.load += B.demand

        self.sol.cost += rm.moveCost

        #self.TestSolution()

    def StoreBestRelocationMove(self, originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex, moveCost, originRtCostChange, targetRtCostChange, rm:RelocationMove):
        rm.originRoutePosition = originRouteIndex
        rm.originNodePosition = originNodeIndex
        rm.targetRoutePosition = targetRouteIndex
        rm.targetNodePosition = targetNodeIndex
        rm.costChangeOriginRt = originRtCostChange
        rm.costChangeTargetRt = targetRtCostChange
        rm.moveCost = moveCost

    def calculate_route_details(self ,nodes_sequence, empty_vehicle_weight):
        tot_dem = sum(n.demand for n in nodes_sequence)
        tot_load = empty_vehicle_weight + tot_dem
        tn_km = 0
        for i in range(len(nodes_sequence) - 1):
            from_node = nodes_sequence[i]
            to_node = nodes_sequence[i+1]
            tn_km += self.distanceMatrix[from_node.ID][to_node.ID] * tot_load
            tot_load -= to_node.demand
        return tn_km, tot_dem

    def TestSolution(self):
        totalSolCost = 0

        for r in range(0, len(self.sol.routes)):
            rt: Route = self.sol.routes[r]
            rtCost, rtLoad = self.calculate_route_details(rt.sequenceOfNodes, 6)  # 6 is the empty_vehicle_weight

            if abs(rtCost - rt.cost) > 0.0001:
                print('Route Cost problem')

            if abs(rtLoad - rt.load) > 0.0001:
                print(rtLoad, rt.load)
                print('Route Load problem')

            totalSolCost += rt.cost

        if abs(totalSolCost - self.sol.cost) > 0.0001:
            print('Solution Cost problem')


def write_to_file(solution, output_file):
    with open(output_file, 'w') as file:
        file.write(f'Cost:\n{solution.cost}\n')
        file.write('Routes:\n')
        file.write(str(len(solution.routes)) + '\n')
        for route in solution.routes:
            route_str = '0'
            for node in route.sequenceOfNodes[1:len(route.sequenceOfNodes)-1]:  # The first node in each route is 0 and should not be repeated
                route_str += ',' + str(node.ID)
            file.write(route_str + '\n')
