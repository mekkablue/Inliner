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
		# Set value of text field
		self.strokeWidthField.setStringValue_(Glyphs.defaults['com.mekkablue.Inliner.strokeWidth'])
		self.inlineWidthField.setStringValue_(Glyphs.defaults['com.mekkablue.Inliner.inlineWidth'])
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
	
	# Actual filter
	@objc.python_method
	def filter(self, layer, inEditView, customParameters):
		# Defaults
		inlineWidth = 10.0
		strokeWidth = 50.0
		
		# Called on font export, get value from customParameters
		if 'stroke' in customParameters:
			inlineWidth = customParameters['stroke']
		# Called through UI, use stored value
		else:
			inlineWidth = float(Glyphs.defaults['com.mekkablue.Inliner.strokeWidth'])

		# Called on font export, get value from customParameters
		if 'inline' in customParameters:
			strokeWidth = customParameters['inline']
		# Called through UI, use stored value
		else:
			strokeWidth = float(Glyphs.defaults['com.mekkablue.Inliner.inlineWidth'])
		
		offsetStroke = (strokeWidth-inlineWidth)*0.25
		offsetParallel = inlineWidth*0.5
		layerL = layer.copyDecomposedLayer()
		layerR = layer.copyDecomposedLayer()
		# shift paths:
		offsetLayer( layerL, -offsetParallel, makeStroke=False, position=0.5, autoStroke=False )
		offsetLayer( layerR,  offsetParallel, makeStroke=False, position=0.5, autoStroke=False )
		# stroke paths:
		offsetLayer( layerL, offsetStroke, makeStroke=True, position=1.0, autoStroke=False )
		offsetLayer( layerR, offsetStroke, makeStroke=True, position=0.0, autoStroke=False )
		# merge them back into main layer:
		layer.clear()
		for thisLayer in (layerL, layerR):
			for thisPath in thisLayer.paths:
				try:
					# GLYPHS 3:
					layer.shapes.append(thisPath.copy())
				except:
					# GLYPHS 2:
					layer.paths.append(thisPath.copy())
	
	@objc.python_method
	def generateCustomParameter( self ):
		return "%s; stroke:%s; inline:%s;" % (
			self.__class__.__name__, 
			Glyphs.defaults['com.mekkablue.Inliner.strokeWidth'],
			Glyphs.defaults['com.mekkablue.Inliner.inlineWidth'],
			)
	
	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
