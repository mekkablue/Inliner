# encoding: utf-8
from __future__ import division, print_function, unicode_literals

###########################################################################################################
#
#
#	Filter with dialog Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Filter%20with%20Dialog
#
#	For help on the use of Interface Builder:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates
#
#
###########################################################################################################

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
from Foundation import NSClassFromString

@objc.python_method
def offsetLayer( thisLayer, offset, makeStroke=False, position=0.5, autoStroke=False ):
	offsetFilter = NSClassFromString("GlyphsFilterOffsetCurve")
	try:
		# GLYPHS 3:	
		offsetFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_metrics_error_shadow_capStyleStart_capStyleEnd_keepCompatibleOutlines_(
			thisLayer,
			offset, offset, # horizontal and vertical offset
			makeStroke,     # if True, creates a stroke
			autoStroke,     # if True, distorts resulting shape to vertical metrics
			position,       # stroke distribution to the left and right, 0.5 = middle
			None, None, None, 0, 0, False )
	except:
		# GLYPHS 2:
		offsetFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_error_shadow_(
			thisLayer,
			offset, offset, # horizontal and vertical offset
			makeStroke,     # if True, creates a stroke
			autoStroke,     # if True, distorts resulting shape to vertical metrics
			position,       # stroke distribution to the left and right, 0.5 = middle
			None, None )

class Inliner(FilterWithDialog):
	# Definitions of IBOutlets
	dialog = objc.IBOutlet()
	
	# Text field in dialog
	strokeWidthField = objc.IBOutlet()
	inlineWidthField = objc.IBOutlet()
	strokeCountField = objc.IBOutlet()
	
	@objc.python_method
	def settings(self):
		self.menuName = u"Inliner"
		
		# Word on Run Button (default: Apply)
		self.actionButtonLabel = u"Stroke"
		
		# Load dialog from .nib (without .extension)
		self.loadNib('IBdialog', __file__)
	
	# On dialog show
	@objc.python_method
	def start(self):
		# Set default value
		Glyphs.registerDefault('com.mekkablue.Inliner.strokeWidth', 50.0)
		Glyphs.registerDefault('com.mekkablue.Inliner.inlineWidth', 10.0)
		Glyphs.registerDefault('com.mekkablue.Inliner.strokeCount', 2)
		# Set value of text field
		self.strokeWidthField.setStringValue_(Glyphs.defaults['com.mekkablue.Inliner.strokeWidth'])
		self.inlineWidthField.setStringValue_(Glyphs.defaults['com.mekkablue.Inliner.inlineWidth'])
		self.strokeCountField.setStringValue_(Glyphs.defaults['com.mekkablue.Inliner.strokeCount'])
		# Set focus to text field
		self.strokeWidthField.becomeFirstResponder()
		
	# Actions triggered by UI:
	# 1. Store value coming in from dialog
	# 2. Trigger redraw
	
	@objc.IBAction
	def setStrokeWidth_( self, sender ):
		Glyphs.defaults['com.mekkablue.Inliner.strokeWidth'] = sender.floatValue()
		self.update()
	
	@objc.IBAction
	def setInlineWidth_( self, sender ):
		Glyphs.defaults['com.mekkablue.Inliner.inlineWidth'] = sender.floatValue()
		self.update()
	
	@objc.IBAction
	def setStrokeCount_( self, sender ):
		strokes = max(1, sender.intValue())
		sender.setStringValue_(str(strokes))
		Glyphs.defaults['com.mekkablue.Inliner.strokeCount'] = strokes
		self.update()
	
	# Actual filter
	@objc.python_method
	def filter(self, layer, inEditView, customParameters):
		# Defaults
		inlineWidth = 10.0
		strokeWidth = 50.0
		strokeCount = 2
		
		# Called on font export, get value from customParameters
		if 'stroke' in customParameters:
			strokeWidth = float(customParameters['stroke'])
		# Called through UI, use stored value
		else:
			strokeWidth = float(Glyphs.defaults['com.mekkablue.Inliner.strokeWidth'])

		# Called on font export, get value from customParameters
		if 'inline' in customParameters:
			inlineWidth = float(customParameters['inline'])
		# Called through UI, use stored value
		else:
			inlineWidth = float(Glyphs.defaults['com.mekkablue.Inliner.inlineWidth'])

		# Called on font export, get value from customParameters
		if 'count' in customParameters:
			strokeCount = int(customParameters['count'])
		# Called through UI, use stored value
		else:
			strokeCount = int(Glyphs.defaults['com.mekkablue.Inliner.strokeCount'])
		
		singleStrokeWidth = (strokeWidth - (strokeCount-1)*inlineWidth) / strokeCount
		
		layerCopy = layer.copyDecomposedLayer()
		layer.clear()
		# Glyphs.clearLog() # clears macro window log
		for i in range(strokeCount):
			singleStrokeLayer = layerCopy.copy()
			firstLineOffset = -strokeWidth*0.5 + singleStrokeWidth*0.5
			currentStrokeOffset = firstLineOffset + i * (singleStrokeWidth + inlineWidth)
			# print(i,currentStrokeOffset)
			
			# shift paths:
			offsetLayer( singleStrokeLayer, currentStrokeOffset, makeStroke=False, position=0.5 )
			
			# stroke paths:
			offsetLayer( singleStrokeLayer, singleStrokeWidth*0.5, makeStroke=True, position=0.5 )
			
			# merge them back into main layer:
			for thisPath in singleStrokeLayer.paths:
				try:
					# GLYPHS 3:
					layer.shapes.append(thisPath.copy())
				except:
					# GLYPHS 2:
					layer.paths.append(thisPath.copy())
	
	@objc.python_method
	def generateCustomParameter( self ):
		return "%s; stroke:%s; inline:%s; count:%s" % (
			self.__class__.__name__, 
			Glyphs.defaults['com.mekkablue.Inliner.strokeWidth'],
			Glyphs.defaults['com.mekkablue.Inliner.inlineWidth'],
			Glyphs.defaults['com.mekkablue.Inliner.strokeCount'],
			)
	
	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
