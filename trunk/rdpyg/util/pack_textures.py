"""

   TODO: need to return UV coordinates and pixel coordinates for the 
     packing/cutting functions for where the images are located on the textures.


   Code to pack multiple textures into larger ones.
   As well as to cut up bigger textures into smaller ones.

   This is useful for eg opengl where there are textures size limits.  Also
    it can speed up rendering as you need to do less texture binding calls,
    and you can reduce geometry calls too.

   Power of 2 textures can be a waste of memory if you have non power of 
    2 sized images.  The more video memory saved the faster a game can go.

   To make this code more useful it will work with rectangles.  So that it can
    be used to update texture memory as well as to update images.


   There will also need to be possibly multiple big output textures.  So that
    you can specify a maximum size output texture.


"""

#import psyco
#psyco.full()



class Texture:
    """ One texture which holds multiple smaller ones packed in.

        x,y bottom left is 0,0.  Which is like opengl, and not like sdl.
    """
    def __init__(self, x,y, height,width):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.sub_textures= []


    def __repr__(self):
        return "<%s,%s,%s,%s>" % (self.x, self.y, self.height, self.width)

    def try_fit(self, other_texture):
        """ Tries to fit the texture into itself.  Returns true if successful.
        """

        if not self.could_fit(other_texture):
            return False

        # an early in.  if there are no other textures, then just put it in.
        if(self.sub_textures == []):
            self.sub_textures.append(other_texture)
            return True


        # Do a search for a place to put it.
        return self.search_for_fit(other_texture)



    def try_fit_batch(self, other_textures):
        """ Tries to fit the textures into itself.  
              Returns true if successful???.  Or returns the unfitted ones?
        """


        # see if they are the same size.

        same_size = 0


        o=other_textures[0]
        x,y,height,width = o.x, o.y, o.height, o.width

        r = filter(lambda oo:(oo.height == height and oo.width == width), 
                   other_textures)
        if len(r) == len(other_textures):
            same_size = 1

        # If they are all the same size, and the texture is empty we
        #  can optimize it.

        unfitted = []

        if same_size and self.sub_textures == []:
            
            # See how many in a row we could fit along the x.
            #  then raise along the y.
            number_on_x = int(round(self.width / width))
            number_on_y = int(round(self.height / height))
            x_pos = 0
            y_pos = 0

            for o in other_textures:
                if(y_pos > number_on_y):
                    # not anymore room.
                    unfitted.append(o)
                else:
                    o.x = x_pos * width
                    o.y = y_pos * height
                    self.sub_textures.append(o)
                    x_pos += 1
                    if(x_pos > number_on_x):
                        y_pos += 1
                        x_pos = 0

        else:
            # TODO: sort the textures into batches of the same size.
            #   could be able to be fairly fast then.
            # try fitting them one at a time.

            for other_texture in other_textures:
                r = self.try_fit(other_texture)
                if not r:
                    unfitted.append(other_texture)


        return unfitted





    def collide(self, other_texture):
        """ checks this texture only to see if it collides.
            Returns True if it does collide.
        """
        sx = self.x
        sy = self.y
        ox = other_texture.x
        oy = other_texture.y

        s_right = sx + self.width
        s_top = sy + self.height

        o_right = ox + other_texture.width
        o_top = oy + other_texture.height



        # check that it is not within the x or y.




        if(ox >= s_right):
           return False

        if(o_right < sx):
           return False

        if(o_top <= sy):
           return False

        if(oy > s_top):
           return False


        return True


    def could_fit(self, other_texture):
        """ checks this texture only to see if it fits.
            Does not care about any textures inside.
        """


        # some early outs.
        if(other_texture.height > self.height):
            return False
        if(other_texture.width > self.width):
            return False


        if(other_texture.x != 0 or other_texture.y != 0 or
           self.x != 0 or self.y != 0):
            # if the x,y is not zero then need to adjust for that.
            s_right = self.x + self.width
            s_top = self.y + self.height

            o_right = other_texture.x + other_texture.width
            o_top = other_texture.y + other_texture.height

            if(o_top > s_top or 
               o_right > s_right or
               other_texture.x < self.x or 
               other_texture.y < self.y):
               return False



        return True

    def search_for_fit(self, o):
        """ do a search for a place to put the texture, and place it.
            Return True if successful, else false.
            o - other texture.
        """
        #TODO: try and optimize this.
        #return self._brute_force(o)
        return self._bottom_left_first(o)




    def _brute_force(self, o):
        """ do a brute force search from bottom left to top right.
            Return True if successful, else false.
            o - other texture.
        """





        x_try = self.x
        y_try = self.y
        x_end = self.x + self.width
        y_end = self.y + self.height

        # go from x_try -> x_end seeing if it fits, 
        #    then increment y_try and go again.

        hits = 0
        for y in range(y_try, y_end):
            for x in range(x_try, x_end):
                o.x = x
                o.y = y
                hits = 0
                for sub in self.sub_textures:
                    # if we can fit inside a sub texture, 
                    #   then we need to keep looking.
                    if sub.collide(o):
                        hits = 1
                        break
                if not hits:
                    break

            if not hits:
                break

        if not hits:
            self.sub_textures.append(o)
            return True
        else:
            return False






    def _bottom_left_first(self, o):
        """ do a search from bottom left.
            Return True if successful, else false.
            o - other texture.
        """


        x_try = self.x
        y_try = self.y
        x_end = self.x + self.width
        y_end = self.y + self.height

        # go from x_try -> x_end seeing if it fits, 
        #    then increment y_try and go again.

        hits = 0
        for y in range(y_try, y_end):
            x = x_try
            while x < x_end:
            #for x in range(x_try, x_end):
                o.x = x
                o.y = y
                hits = 0
                for sub in self.sub_textures:
                    # if we can fit inside a sub texture, 
                    #   then we need to keep looking.
                    if sub.collide(o):
                        hits = 1
                        # move accross to the x of the sub.
                        x = sub.x + sub.width
                        break
                if not hits:
                    break

                x += 1

            if not hits:
                break

        if not hits:
            self.sub_textures.append(o)
            return True
        else:
            return False



    def clear(self):
        """ clears all the textures in this one.
        """
        self.sub_textures= []




def pack_images_into_multiple(small_list, max_size, use_pow2 = 1):
    """ returns a list of Texture objects with the textures from the small_list
         packed into them.
        small_list - list of Texture objects
        max_size - of the output Textures.
        use_pow2 - if 0 then we do not have to limit ourselves to power of 2.
    """
    raise NotImplementedError



def split_big_image(big_image, max_size, use_pow2 = 1):
    """ returns a list of Textures which the big_image is split into.
        big_image - a Texture object.

        TODO: how to determine where the small bits are placed?
    """
    raise NotImplementedError




