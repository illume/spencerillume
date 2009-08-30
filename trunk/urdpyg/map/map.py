"""
= Features wanted =
 * When not moving it can take only update parts of the screen.
 * update(dirty_rects) can be used to speed up drawing.
   * by only updating areas which are dirty.
   * if the map is not moving we can make it lots speedier.

 * Offscreen buffer.  Blit all smaller tiles to an offscreen buffer then blit 
   one big image to the screen.  This can be faster on some screens/computers.
 * Different tile sizes.
   * different sizes on the same map.
 * Join maps together easily.
 * Different drawable sizes.  Ie different camera views.
 * Be able to be used with pygame or pyopengl.
 * Different camera modes: 
   * jump scrolling, 
     * jump the map in blocks.  Like ten pixels at a time.
   * smooth scrolling, 
     * every pixel the camera moves the tiles move.
   * smooth-jump scrolling.  
     * Mostly the screen stays still.  When the character nears the edge 
       everything stops moving while the maps scrolls over a little way.
   * centered camera.
     * Can center the camera on 
   * Looping Map Edges
   * Paralax scrolling.
     * Moving layers at different speeds.
   * Multiple views of the map.
   * miniview of the map.  Perhaps using a scaled version or one pixel per tile.

* minimize overdraw.
  * using dirty rectangles.
  * for alpha images precalculate 'full rects'.  
    * That is like a bounding box in the middle where the area is full.
  * think about using a coverage buffer.
  * animated tiles will probably always need to be redrawn(unless it's the same frame).

* Overlapping tiles.
  * As well as overlapping whole maps.  For joining maps together.
* Layers/Z ordering.
  * draw characters by descending y value on same layer.
    * for certain types of games:  see for explanation:
        * http://www.gamedev.net/reference/programming/features/gpgenesis9/page7.asp

* line of sight tests between tiles and pixels/rects.
* collision detection between tiles and pixels/rects.
  * some tiles may be pass through.
  * tiles on different layers may be collidable, others not.

* fog of war.
    * darkening/lightening of areas.

* Rotatable tiles.
  * scalable tiles?  Other transforms needed?


* Easy layer toggling.
  * So eg when you go inside a building the roof comes off and you can see inside.




= Implementation ideas =

* Use pygame sprites and sprite groups.
  * could then reuse lots of code...  optimize in one place.  Speed development.
  * think of camera movement as simply moving a sprite group in a certain way.

* Use a quad tree for the collision detection.
  * Could use it for moving, and non moving.

* Left to right, or top to bottom scrollers can be optimized in different ways.




= Some map editors =

The tile combie(or engine if you want) should have most of the features that these map editors contain.

http://tilestudio.sourceforge.net/


http://www.tilemap.co.uk/






= A discussion about features =




<geoffh> background tiling, layers, collision detection between layers and stuff (rect and pixel)
<geoffh> paralax scrolling
<geoffh> animation of background/sprites
<geoffh> line of sight tests between tiles and pixels
<geoffh> based on layer compositions and such
<illumeh> eek, that's a lot of stuff
<illumeh> good stuff :)
<geoffh> separate environmental and UI layer systems
<illumeh> what do you mean?
<geoffh> so you can draw your UI without worrying how height your environments layers are
<geoffh> the UI layers are alwayrs on top
<illumeh> ah, cool
<geoffh> basically, just 2 lists for heights
<geoffh> auto-shadowing for sprites is good
<illumeh> indeed, that'd be cool
<geoffh> doing like angled skews on the images, and drawing them on the ground layer
<geoffh> so you dont have to have separate shadow images for them
<illumeh> nice
<geoffh> or just auto positioning the same image, but based on heigth of the sprite

<geoffh> so like a flying ship has its shadow in the real place, and its in its height-adjusted place,  like zaxxon
<geoffh> which basically just means you have a transformation for height built in, and use a sort of worrld coords and translated drawing coords
<illumeh> aah
<geoffh> which makes sense
<geoffh> so you should have parameters to what your viewing perspective is, so they can adjust it based on how their art is rendered
<geoffh> like:  1.5:1.0 or something

<geoffh> you could also have layer toggling like i did in VT, where if you go into a building, it switches what the background tiles are.  and if you change floors, it also does that
<illumeh> ah, that sounds nice too
<geoffh> but that may be a bit specific.  though, you could make the design so its possible to rotate through BG tile maps specifically, like theyre layered and do a fall through if the current selected one doesnt exist
<geoffh> to the default background map, which has all its spaces mapped
<geoffh> sorta an "optional current level background"
<geoffh> good for things where people take stairs, and you still want the ground of things outside buildings and such
<geoffh> im running out of stuff ive thought about for tiling engines
<illumeh> hehe.  that's all stuff I didn't think about :)
<geoffh> i want to retire
<geoffh> im pretty happy doing fuck all all the time now
<geoffh> heh
<illumeh> having layers greyed out would be good
<illumeh> hehe.  mostly I'm happy doing fuck all too :)
<geoffh> optional layers?  or you mean something else?


"""




