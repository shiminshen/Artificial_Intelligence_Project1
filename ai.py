import random
import time
import multiprocessing
import numpy as np
import Queue
import heapq

class ai_agent():
	mapinfo = []
	def __init__(self):
		self.mapinfo = []

	# rect:					[left, top, width, height]
	# rect_type:			0:empty 1:brick 2:steel 3:water 4:grass 5:froze
	# castle_rect:			[12*16, 24*16, 32, 32]
	# mapinfo[0]: 			bullets [rect, direction, speed]]
	# mapinfo[1]: 			enemies [rect, direction, speed, type]]
	# enemy_type:			0:TYPE_BASIC 1:TYPE_FAST 2:TYPE_POWER 3:TYPE_ARMOR
	# mapinfo[2]: 			tile 	[rect, type] (empty don't be stored to mapinfo[2])
	# mapinfo[3]: 			player 	[rect, direction, speed, Is_shielded]]
	# shoot:				0:none 1:shoot
	# move_dir:				0:Up 1:Right 2:Down 3:Left 4:None
	# keep_action:			0:The tank work only when you Update_Strategy. 	1:the tank keep do previous action until new Update_Strategy.

	# def Get_mapInfo:		fetch the map infomation
	# def Update_Strategy	Update your strategy


			
			
	def operations (self,p_mapinfo,c_control):	

		while True:
		#-----your ai operation,This code is a random strategy,please design your ai !!-----------------------			
			self.Get_mapInfo(p_mapinfo)
			# print self.mapinfo[3]
			# time.sleep(0.05)	
			
			# q=0
			# for i in range(10000000):
			# 	q+=1
			
			# shoot = random.randint(0,1)
			# move_dir = random.randint(0,4)

			#keep_action = 0
			keep_action = 1
                        if not self.canShoot(self.mapinfo[3][0], ''):
                            self.Update_Strategy(c_control, 0, 4, keep_action)

                        mapMatrix = self.convertMap2List(self.mapinfo[2])
                        move_dir, shoot = self.getStrategy(mapMatrix, self.mapinfo)

			#-----------
			self.Update_Strategy(c_control,shoot,move_dir,keep_action)
		#------------------------------------------------------------------------------------------------------

        def heuristicMap(self, envMap, selfTank, enemyTank, bullets, enemies):
            """get the heuristic cost map

            :envMap. selfPosition: TODO
            :enemyPosition: TODO
            :bullets: TODO
            :enemies: TODO
            :returns: TODO

            """

            costMap = envMap.copy()
            # compute heuristic cost into cost map
            for index, obType in np.ndenumerate(costMap):
                # convert obstacle to max cost value
                if obType == 2 or obType == 3 or obType == 1:
                    costMap[index] = 9999
                    continue
                # fill heuristic cost into valid path
                else:
                    enemyPosition = (enemyTank[0].top, enemyTank[0].left)
                    costMap[index] = self.heuristicDistance(index, enemyPosition) 
                    # costMap[enemyPosition] += 50

            # print bullets
            # add bullets penalty
            for bullet in bullets:
                dangerPoint = bullet[0].move(-8, -8)
                # check the bound of map
                if self.isOutOfBound(dangerPoint.top) or self.isOutOfBound(dangerPoint.left):
                    dangerPoint = bullet[0]

                dangerPoint.width *= 10 
                dangerPoint.height *= 10 

                direction = bullet[1]

                self.addPenalty(costMap, dangerPoint, direction, 500)


            # add bullets warning penalty
            for bullet in bullets:
                dangerPoint = bullet[0].move(-16, -16)
                # check the bound of map
                if self.isOutOfBound(dangerPoint.top) or self.isOutOfBound(dangerPoint.left):
                    dangerPoint = bullet[0]

                dangerPoint.width *= 20
                dangerPoint.height *= 20

                direction = bullet[1]

                self.addPenalty(costMap, dangerPoint, direction, 300)

            # add enemies penalty
            for enemy in enemies:
                dangerPoint = enemy[0]
                # check the bound of map
                if self.isOutOfBound(dangerPoint.top) or self.isOutOfBound(dangerPoint.left):
                    dangerPoint = enemy[0]

                direction = enemy[1]

                self.addPenalty(costMap, dangerPoint, direction, 300)

            # add enemies warning penalty
            for enemy in enemies:
                dangerPoint = enemy[0].move(enemy[0].width, enemy[0].height)
                # check the bound of map
                if self.isOutOfBound(dangerPoint.top) or self.isOutOfBound(dangerPoint.left):
                    dangerPoint = enemy[0]

                dangerPoint.width *= 3
                dangerPoint.height *= 3

                direction = enemy[1]

                self.addPenalty(costMap, dangerPoint, direction, 100)



            # np.savetxt('map.csv', costMap, fmt='%d', delimiter=',')
            return costMap

        def addPenalty(self, mapMatrix, bulletRect, direction, penalty):
            """add the penalty on the trajectory of bullet

            :mapMatrix: TODO
            :bulletRect: TODO
            :direction: TODO
            :penalty: TODO
            :returns: TODO

            """

            bulletTop    = bulletRect.top
            bulletLeft   = bulletRect.left
            bulletWidth  = bulletRect.width
            bulletHeight = bulletRect.height

            # print 'bullet tragecotry----------------'
            if direction == 0:
                # move up
                mapMatrix[:bulletTop+bulletHeight, bulletLeft: bulletLeft+bulletWidth] += penalty
                # print '0:' + str(bulletTop) + ' ' + str(bulletLeft) + ':' + str(bulletLeft+bulletWidth)
            elif direction == 1:
                # move right
                mapMatrix[bulletTop:bulletTop+bulletHeight, bulletLeft+bulletWidth:] += penalty
                # print str(bulletTop) + ':' + str(bulletTop+bulletHeight) + ' ' + str(bulletLeft+bulletWidth) + ':'
            elif direction == 2:
                # move down
                mapMatrix[bulletTop+bulletHeight:, bulletLeft: bulletLeft+bulletWidth] += penalty
                # print str(bulletTop) + ':' + ' ' + str(bulletLeft) + ':' + str(bulletLeft+bulletWidth)
            elif direction == 3:
                # move left
                mapMatrix[bulletTop:bulletTop+bulletHeight, :bulletLeft+bulletWidth] += penalty
                # print str(bulletTop) + ':' + str(bulletTop+bulletHeight) + ' :' + str(bulletLeft+bulletWidth)
            else:
                pass
            return mapMatrix
            

        def canShoot(self, selfInfo, mapMatrix):
            """current information of self tank

            :selfInfo: TODO
            :mapMatrix: TODO
            :returns: TODO

            """

            currPositionRect = selfInfo[0]
            # currPositionRect = self.getNextStep(selfInfo[0], selfInfo[1], 12)

            self_x         = currPositionRect.left
            self_y         = currPositionRect.top
            self_width     = currPositionRect.width
            self_height    = currPositionRect.height
            self_direction = selfInfo[1]

            castle = [192, 384, 32, 32]
            # if self_y > 345 and (self_direction == 1 or self_direction == 3):
            if self_y > 345:
                # print 'not Shoot'
                return 0
            # if self_x > 148 and self_x < 250 and (self_direction == 2):
            if self_x > 148 and self_x < 250:
                print 'not Shoot'
                return 0

            return 1

            
        def getAllDirectionCost(self, selfInfo, costMap, step = 8):
            """get cost of all moving directions

            :selfInfo: TODO
            :returns: TODO

            """

            # currPositionRect = self.getNextStep(selfInfo[0], selfInfo[1], 12)
            # currPositionRect = selfInfo[0]
            currPositionRect = selfInfo

            topPoint = currPositionRect.move(0, -step)
            rightPoint = currPositionRect.move(step, 0)
            bottomPoint = currPositionRect.move(0, step)
            leftPoint = currPositionRect.move(-step, 0)

            topValue = self.getAvgCost(topPoint, costMap)
            rightValue = self.getAvgCost(rightPoint, costMap)
            bottomValue = self.getAvgCost(bottomPoint, costMap)
            leftValue = self.getAvgCost(leftPoint, costMap)
            
            # print 'Direction'
            # print currPostionRect

            print '----------------'
            print topValue
            print rightValue
            print bottomValue
            print leftValue

            return [topValue, rightValue, bottomValue, leftValue]

        def isOutOfBound(self, index):
            """check the index of position does not exceed the bound of map

            :index: TODO
            :returns: TODO

            """
            if index > 390 or index < 0:
                return 1

            return 0

        def getAvgCost(self, positionRect, costMap):
            """get average cost in position rectangle

            :positionRect: TODO
            :costMap: TODO
            :returns: TODO

            """
            top    = positionRect.top
            left   = positionRect.left

            width  = positionRect.width
            height = positionRect.height

            # width  = positionRect.width / 2
            # height = positionRect.height / 2

            if self.isOutOfBound(top) or self.isOutOfBound(left):
                return 9999
            else:
                frontInfo = costMap[top:top+height, left:left+width]
                # print 'Number of obstacle: ' + str(frontInfo[frontInfo == 9999].size)
                if frontInfo[frontInfo == 9999].size > 100:
                    return 9999

                # return np.average(frontInfo)
                return np.amin(frontInfo)

        def heuristicDistance(self, p1, p2):
            """get the distance between to point p1 and p2

            :p1: point1
            :p2: point2
            :returns: int: distance of two point

            """
            return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

        def getNearestEnemy(self, user, enemies):
            """get the nearest enemy

            :user: User current position
            :enemies: All enemies information
            :returns: The nearest enemy

            """
            nearestEnemy = None
            minDist = 416 * 2
            userPosition = (user[0].top, user[0].left)
            castle = [192, 384, 32, 32]
            castlePosition = (384, 192)

            for enemy in enemies:

                enemyPosition = (enemy[0].top, enemy[0].left)
                # calculate the distance to enemy
                distance = self.heuristicDistance(userPosition, enemyPosition)
                # distance = 0.2 * self.heuristicDistance(userPosition, enemyPosition) + 0.8 * self.heuristicDistance(enemyPosition, castlePosition)
                # print 'dist: ' + str(distance)

                # update nearest enemy
                if distance < minDist:
                    nearestEnemy = enemy
                    minDist = distance

            return nearestEnemy

        def getNextStep(self, positionRect, direction, step = 8):
            """estimate the next position from current moving direction

            :positionRect: TODO
            :direction: TODO
            :returns: TODO

            """

            if direction == 0:
                return positionRect.move(0, -step)
            elif direction == 1:
                return positionRect.move(step, 0)
            elif direction == 2:
                return positionRect.move(0, step)
            elif direction == 3:
                return positionRect.move(-step, 0)
            else:
                return positionRect

        def getStrategy(self, mapMatrix, mapInfo):
            """detemine the strategy about moveing direction and shooting or not

            :mapMatrix: Environment map. Each value is a pixel in the map
            :mapInfo: All information about map
            :returns: Array[moving direction, shoot]

            """

            selfInfo    = mapInfo[3][0]
            bulletsInfo = mapInfo[0]
            enemiesInfo = mapInfo[1]

            print selfInfo
            # get the nearest enemy to my tank
            enemy = self.getNearestEnemy(selfInfo, enemiesInfo)

            validDirection = []
            movingDirection = 4
            if enemy:
                costMatrix = self.heuristicMap(mapMatrix, selfInfo, enemy, bulletsInfo, enemiesInfo)
                directionCost = self.getAllDirectionCost(selfInfo[0], costMatrix, 8)
                print 'self direction: ' + str(selfInfo[1])
                minCost = min(directionCost)
                for index, cost in enumerate(directionCost):
                    if cost == minCost or cost < 30:
                        validDirection.append(index)
                        # break
                random.shuffle(validDirection)
                print validDirection
                self.AStar(selfInfo[0], enemy[0], costMatrix)
            # random select best step
            if len(validDirection) > 0:
                movingDirection = validDirection[0]

            # print 'move direction: ' + str(movingDirection)
            return (movingDirection, self.canShoot(selfInfo, mapMatrix))

        def convertMap2List(self, envInfo):
            """convert environment of map info to list

            :mapinfo: All information about map
            :returns: Numpy.array

            """
            # initialzie map
            mapMatrix = np.zeros((416, 416), dtype=np.int)

            # fill obstacle into map
            for block in envInfo:
                pixelState = [block[0].top, block[0].left, block[1]]
                topPixel = block[0].top
                leftPixel = block[0].left
                # fill nonempty pixel in the map
                for vOffset in xrange(0, block[0].height):
                    for hOffset in xrange(0, block[0].width):
                        mapMatrix[topPixel + vOffset, leftPixel + hOffset] = block[1]

            # np.savetxt('map.csv', mapMatrix, fmt='%d', delimiter=',')
            return mapMatrix

        def AStar(self, startRect, enemyRect, costMap):
            """compute shortest path by A star algorithm

            :startRect: TODO
            :enemyRect: TODO
            :costMap: TODO
            :returns: TODO

            """

            # initialize the heap
            openSet = []
            heapq.heapify(openSet)
            closedSet = set()
            # heapq.heappush(openSet, (costMap[startRect.top, startRect.left], startRect))
            startNode = Node(startRect, costMap[startRect.top, startRect.left])
            heapq.heappush(openSet, (startNode.heuristicCost, startNode))

            while len(openSet) > 0:
                # pop the lowest cost
                currNode = heapq.heappop(openSet)[1]
                closedSet.add(currNode)
                print 'pop: '
                print currNode.rect
                print len(closedSet[0])

                # print 'node-----------------'
                # print currNode.rect
                # print 'enemy----------------'
                # print enemyRect
                # print 'heuristic: ' + str(currNode.heuristicCost)

                # return path if reach the goal
                # if currNode.rect == enemyRect:
                if currNode.rect.top == enemyRect.top and currNode.left == enemyRect.left:
                    print 'found'
                    return

                # get cost of all directions
                allDirectionCost = self.getAllDirectionCost(currNode.rect, costMap, 10)
                
                for index, cost in enumerate(allDirectionCost):
                    nextNode = Node(self.getNextStep(currNode.rect, index, 10), cost)
                    if nextNode in closedSet:
                        continue

                    if nextNode.heuristicCost < currNode.heuristicCost:
                        print 'move to '
                        print nextNode.rect
                        nextNode.parent = currNode
                        heapq.heappush(openSet, (nextNode.heuristicCost, nextNode))

                    if nextNode not in openSet:
                        heapq.heappush(openSet, (nextNode.heuristicCost, nextNode))
                    
                # break
                        

	def Get_mapInfo(self,p_mapinfo):
		if p_mapinfo.empty()!=True:
			try:
				self.mapinfo = p_mapinfo.get(False)
			except Queue.Empty:
				skip_this=True

	def Update_Strategy(self,c_control,shoot,move_dir,keep_action):
		if c_control.empty() ==True:
			c_control.put([shoot,move_dir,keep_action])
			return True
		else:
			return False

class Node(object):
    """abstrct class for recording a star result"""
    def __init__(self, rect, heuristicCost):
        super(Node, self).__init__()
        self.rect, self.heuristicCost = rect, heuristicCost
        self.parent = None
        
