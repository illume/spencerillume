# file: virtual_timer.py
# purpose: to be able to do things once a time is up.
#     or to keep track of something which lasts a given time.





class vtimer:
    """ times something.  when it is done it is equal to 1, else equal to 0.
        
        Useage:
          v = VirtTimer(5.)
          if v:
              dosomething()
          v.Update(elapsed_time)

          OR with a callback.

          v = VirtTimer(5., dosomething)
          v.Update(elapsed_time)

        Call Update on each game tick.  Passing in elapsed time in seconds 
         allows you to have timers running on different time.  So pausing, 
         and things like bullet time are easy.


        Also has some other features.
          You can be notified on the "edge" of time.  That is when a timer
          is just_started or just_finished.

          if v.just_finished:
              do_some_other_thing()

          You can find how much time is left.  As well as get a normalised 
          amount of time left(between 0. and 1.).

          eg. time_before_powerup_runs_out = powerup_timer.left()
    """
    def __init__(self, length, callback = None):
        """ length - of time to run for.
            callback - optional callback function to call.
        """
        self.length = length
        self.callback = callback

        self.reset()

        self.update = self.Update
        self.is_not_used = 0


    def Update(self, elapsed_time):
        """Update(1.0) -> None
           To be called on every game tic.
           elapsed_time - since last update.
        """

        if self.just_started:
            self.just_started = 0
        if self.just_finished:
            self.just_finished = 0


        self.total_elapsed_time += elapsed_time

        if self.total_elapsed_time >= self.length:
            if self.done == 0:
                self.just_finished = 1
            self.done = 1

            if self.callback != None:
                if not self.called_callback:
                    self.callback()
                    self.called_callback = 1




    def reset(self):
        """ reset() -> None
            Resets the timer to the beginning.
        """

        self.total_elapsed_time = 0.
        self.done = 0
        self.called_callback = 0
        self.just_started = 1
        self.just_finished = 0
        self.is_not_used = 0


    def set_finished_no_callback(self):
        """ set_finished_no_callback() -> None

            Sets it to finished, without calling callback.  not just finished.
        """
        self.total_elapsed_time = 10000000000000L
        self.done = 1
        self.called_callback = 1
        self.just_started = 0
        self.just_finished = 0
        self.is_not_used = 1


    def not_used(self):
        """ not_used -> None
            
            For if the timer is not being used.  This is useful for one time,
              timers.
        """
        self.is_not_used = 1

    # equality methods used for testing the timer.


    def __eq__(self, other):
        return self.done == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __nonzero__(self):
        return self.done


    def left(self):
        """ left() -> time left until finished.
        """
        left = self.length - self.total_elapsed_time
        if left < 0.:
            return 0.
        else:
            return left


    def left_normalised(self):
        """ left_normalised() -> the time left normalized to 0. - 1.
        """
        left = self.left()
        if left == 0.:
            return 0.
        else:
            return (1. / self.length) * left




