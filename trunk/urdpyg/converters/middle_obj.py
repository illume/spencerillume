"""
    Copyright (C) 2002 by Rene Dudfield.
  
    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Library General Public
    License as published by the Free Software Foundation; either
    version 2 of the License, or (at your option) any later version.
  
    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Library General Public License for more details.
  
    You should have received a copy of the GNU Library General Public
    License along with this library; if not, write to the Free
    Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""


"""

A scene graph which will contain all sorts of information about 3d scenes.

Advantages this method will give you.    
    - Allow importers and exporters to be written independantly.  Just
        write an importer and you can take advantage of all the exporters.
    - Able to choose a disk based, or memory based conversion.
    - Don't have to support all of a 3d format, can support only parts of a 
        format.  This is necessary as development nearly always happens 
	incrementally with 3d format converters.    This means importers and 
	exporters will have to specify which elements that they support.
    - Extensibility: the system is designed to be extensible.  So that if new
        3d formats are added they will not affect the old ones.  This is done 
	by having all importers and exporters contain a list of features which
	they support.
	
	Here is an example of how it would all work:
	First the importer and exporter(s) will tell the middle object which
	features that they support(or are interested in).
	
	The importer will read in what of the 3d format it understands, then
	pass the 3d data onto the middle object.  Also passing on the features
        which the importer has imported.  
    - Support multiple exporters being used at once.  But only one importer 
      being used at once.  Multiple exporters will be useful to save having 
      to do the import step multiple times when exporting to lots of formats.
      
    - Each exporter will be responsible for setting which features that it 
      wants to export.  That way it is possible to 
    - A feature can be any sort of 3D data.  We want to support as much 
      different data as possible.  
      
      Here is a list of 3d data that I can think of:
	  = mesh data, 
	    = vertex, face lists.
	    = vertex shading information.
	    = per vertex, pre face UV information.
	    
	  = Scene graph information( this will be hard ).
	    - It could be a graph of indicies to other objects.
	      Maybe a tuple of (feature_name, index into list)
	    - Not sure how inheritance will be handled.
	    
	  = bezier lines, and patches.
	  = nurb lines and patches.
	  = Texture mapping info.
	  = cameras
	  = lights (point, spot, omni, ambient).
	  = image maps for terrain.
	  = Material information.
	    - color maps.
	    - animations.
	    - bump maps.
	    - alpha maps.
	    - smoothing.
	    - specularity.
	    
	    
    - May provide a heap of helper functions, to help make converting the
      data easier.  Providing different views of the intermediate data. eg.
      converting a mesh made up of 4, and 3 sided polygons into a mesh made up
      of only 3 side polygons.  
      
      Here is a list of helpers:
	  = ngons to triangles.
	  = curve patches to triangles.
	  = per face, to per vertex uv mapping conversions.
	  = scaling.
	  = rotation.
	  = converting which coordinates are up, sideways and depth.
	  
    - May need to implement a disk based dictionary, and a disk based list.
      As the shelf object which uses a database as a backend is pretty lame.
      It can only store objects of a certain size.  Also they are only 
      dicts, not lists.
    
    - Perhaps to save on memory, we could write certain features to 
      disk(using pickle) whilst the other data is being converted.
    
    
    - Importers, and exporters don't necessarily need to read or write to 
      files.  eg. They may comunicate directly with a 3d editor, or a game 
      engine.  They could use a COM, CORBA, or xml rpc interface.
      
    - Should try and make use of other converter libraries, eg lib3ds.
    - importers and exporters should be able to do things like eg. only export 
      frame 34 of the animation.  Probably have to expand on the feature 
      passing idea for this.

  
  Diagram of how feature information moves around:
      
      
      user --wanted exporters--> middle_obj
      user --wanted features for exporters--> middle_obj
      user --wanted features--> middle_obj
      
      importer --supported features--> middle_obj 
      
      middle_obj --features to export--> exporters
     
    - Reduce the number of unnessesary calculations.  One way to do this is to
      have the importers and exporters know which way certain things are 
      defined.  Eg. the coordinate systems: in one format x may be depth, and 
      in another format x may be depth but comming into the screen.
      
      ei. if two formats both use z+ as depth then there is no need to 
      transform the coordinates when putting them into the middle object.

      NOTE: supplying all different types of stores in the middle object should
      not be mandatory.  There will be a default for the middle object which 
      all importers should support.

      NOTE: This information would be stored with each feature.  Eg,
        Meshes.Triangles.PointOrder.Supported.Value = ["clockwise", "anticlockwize"]
        Meshes.Triangles.PointOrder.Default.Value = "clockwise"


    - If Conversions have to be done on data, make sure that the conversions 
      also change other data which is dependant on it.  The only example of 
      this that I can think of at the moment is Indexes to things.  eg.
       face list index to a heap of points.

      Maybe we should keep some dependancy information somewhere.  Think
      about this some more.  Maybe too much effort.
    
    - Keep documentation of all the features.

      Documentation of every feature will be kept in a master feature list.
      The master feature list will be generated from the importers,exporters,
      and the middle object.  The middle object will be updated sporadically 
      when new features come around.

      The documentation of the features will also be taken from 

    - Keep a central repository of all the different features.  Supply a
      report of which importers/exporters support what.  These need to be 
      automated.

      The feature objects of a importer/exporter/middle_object are python 
      objects which contain __doc__ strings.
    

    - With (importers/exporters) and the middle object, the feature objects 
      are used differently.  The middle object uses features to store not only
      the documentation on the various features, but also data itself.
      
    - Make some test importers, and exporters.  A test importer will fill up
      the middle object with what ever data the exporter asks of it.
      A test exporter will ask the middle object for some data to export.
      If we can get an test exporter, and importer which supports _ALL_ the
      features, then testing will be easier, and there will be some base 
      implementations for people to look at.

    - A validate format function for each format may be useful.  One function
      could be used to validate the import and export plugins.  

      It is optional to implement this.  Quality plugins implement this ;).

    - A DoValidation() method for importers and exporters may be useful.  This 
      way an importer/exporter has the option of validating the data or not.
      Not validating the data may be a speed increase.  Both in speeding
      up the conversion and speeding up the writing of the plugin.  Validating
      data during the conversion may also be faster than doing the validation 
      as a seperate pass.

      It is optional to implement this.  Quality plugins implement this ;).

"""



    
class MiddleObject:
    
    def __init__(self):
	""" """
	
	# A dictionary of features
	self.features = {}
	
        
    def AddImporter(self, importer):
	""" importer - an object used to import 3d data into the middle object.
	"""
	
	
    def AddExporter(self, exporter):
	""" exporter - an object used to export 3d data from the middle object.
	"""
	
    def SendFeatureRequestsToImporter(self):
	""" Goes through the exporters and gathers a set of 
	    features which need to be sent to the importer.
	"""
    
    



class Importer:
    """ Used for importing 3d data into a MiddleObject.
        This is a base class, to be used for importers for various
	3d formats.
    """
    
    def __init__(self, supported_features, wanted_features = {}):
	""" supported_features - features which the 
	    wanted_features - defaults to all features if not specified.
	"""
	
	self.supported_features = supported_features
	self.wanted_features = wanted_features
	
	
    def GetSupportedFeatures(self):
	""" Returns the features that this importer supports."""
	return self.supported_features
    
    
    def SetFeaturesWanted(self, features):
	""" Used to tell the importer what features the importer should
	    pass onto the middle object.
	    NOTE: this does not mean that the importer should not load all
	    of the 3d format.  If it has to load it all so be it.  Just pass
	    the features that are wanted.
	"""
	self.wanted_features = features
    	
	
    def Start(self):
	""" Starts the importer doing its import thing."""
	raise "This importer is missing an implementation of Start()"
	
    
    
    
    
    
	
    
class Exporter:
    """ Used for exporting 3d data from the MiddleObject.
        This is a base class, to be used for exporters for various
	3d formats.
    """
    
    
    def __init__(self, supported_features, wanted_features = {}):
	""" supported_features - """
	
	self.supported_features = supported_features
	self.wanted_features = wanted_features
    
    
    
    def GetSupportedFeatures(self):
	""" Returns the features that this exporter supports."""
	return self.supported_features
    
    
    def SetFeaturesWanted(self, features):
	""" Used to tell the exporter what features the exporter should
	    get from the middle object.
	"""
	self.wanted_features = features
    
    
    
    
    
    
    
    
    
