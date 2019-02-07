# Quadtree implementation for collision detection
import pygame

def triangle_area(triangle):
	x1 = triangle[0][0]
	y1 = triangle[0][1]
	x2 = triangle[1][0]
	y2 = triangle[1][1]
	x3 = triangle[2][0]
	y3 = triangle[2][1]

	return abs((x1*(y2-y3) + x2*(y3-y1)+ x3*(y1-y2))/2)

def point_in_triangle(point, triangle):
	total_area = triangle_area(triangle)

	triangle_1 = (point, triangle[1], triangle[2])
	area_1 = triangle_area(triangle_1)

	triangle_2 = (triangle[0], point, triangle[2])
	area_2 = triangle_area(triangle_2)

	triangle_3 = (triangle[0], triangle[1], point)
	area_3 = triangle_area(triangle_3)

	return (total_area == area_1+area_2+area_3)

class CentreRect():
	"""docstring for CentreRect"""
	def __init__(self, x, y, w, h):
		super(CentreRect, self).__init__()
		self.x = x
		self.y = y
		self.w = w
		self.h = h

		self.points = [(self.x-self.w, self.y-self.h), (self.x+self.w, self.y-self.h), (self.x-self.w, self.y+self.h), (self.x+self.w, self.y+self.h)]

	def contains(self, point):
		return (point[0] >= self.x - self.w and
			point[0] <= self.x + self.w and
			point[1] >= self.y - self.h and
			point[1] <= self.y + self.h)

	def intersects(self, shape, triangle):
		if not triangle:
			shape = shape.points

		for point in shape:
			if self.contains(point):
				return True

		# An additional check is needed if shape is a triangle
		if triangle:
			for point in self.points:
				if point_in_triangle(point, shape):
					return True

		return False

class NormalRect():
	"""docstring for NormalRect"""
	def __init__(self, points):
		super(NormalRect, self).__init__()
		self.points = points
		self.x = self.points[0][0]
		self.y = self.points[0][1]
		self.w = self.points[3][0]
		self.h = self.points[3][1]

	def contains(self, point):
		return (point[0] >= self.x and
			point[0] <= self.w and
			point[1] >= self.y and
			point[1] <= self.h)

	def intersects(self, shape, triangle):
		if not triangle:
			shape = shape.points

		for point in shape:
			if self.contains(point):
				return True

		# An additional check is needed if shape is a triangle
		if triangle:
			for point in self.points:
				if point_in_triangle(point, shape):
					return True

		return False
		

class Quadtree():
	"""docstring for Quadtree"""
	def __init__(self, bounds, capacity):
		super(Quadtree, self).__init__()
		self.bounds = bounds
		self.capacity = capacity # Max number of particles in a subdivision
		self.points = []
		self.divided = False

	def draw(self, surface):
		pygame.draw.rect(surface, (255, 0, 0), (self.bounds.x-self.bounds.w, self.bounds.y-self.bounds.h, self.bounds.w+self.bounds.w, self.bounds.h+self.bounds.h), 1)
		if self.divided:
			self.ne.draw(surface)
			self.nw.draw(surface)
			self.se.draw(surface)
			self.sw.draw(surface)

	def insert(self, point):
		if not self.bounds.contains(point):
			return False

		if len(self.points) < self.capacity:
			self.points.append(point)
			return True
		else:
			if not self.divided:
				self.subdivide()
			
			if self.ne.insert(point):
				return True
			elif self.nw.insert(point):
				return True
			elif self.se.insert(point):
				return True
			elif self.sw.insert(point):
				return True

	def subdivide(self):
		x = self.bounds.x
		y = self.bounds.y
		w = self.bounds.w
		h = self.bounds.h

		self.ne = Quadtree(CentreRect(x + w/2, y - h/2, w/2, h/2), self.capacity)
		self.nw = Quadtree(CentreRect(x - w/2, y - h/2, w/2, h/2), self.capacity)
		self.se = Quadtree(CentreRect(x + w/2, y + h/2, w/2, h/2), self.capacity)
		self.sw = Quadtree(CentreRect(x - w/2, y + h/2, w/2, h/2), self.capacity)

		self.divided = True

	def query(self, shape, triangle=False):
		found = []
		if not self.bounds.intersects(shape, triangle):
			return found
		
		else:
			for p in self.points:
				if not triangle:
					if shape.contains(p):
						found.append(p)
				else:
					if point_in_triangle(p, shape):
						found.append(p)

			if self.divided:
				found += self.ne.query(shape, triangle)
				found += self.nw.query(shape, triangle)
				found += self.se.query(shape, triangle)
				found += self.sw.query(shape, triangle)

			return found