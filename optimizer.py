
import numpy as np
from scipy.signal import find_peaks, freqz

# Define constants for the optimization process
threshold_dB = -3

class FireFly:
    def __init__(self, Thread, L, beta, freqResolution, n_pop, max_iter, gamma, alpha, lamda):
        self.Thread = Thread  
        self.L = L  
        self.beta = beta 
        self.freqResolution = freqResolution 
        self.n_pop = n_pop 
        self.max_iter = max_iter
        self.gamma = gamma  
        self.alpha = alpha 
        self.lamda = lamda  
        self.window_rec = np.ones(L)
        self.mw_rec = self.calculate_mw(self.window_rec)

        self.window = np.kaiser(L, beta)
        self.mw = self.calculate_mw(self.window)

    def symmetric_window(self, window):
        """
        Constructs a symmetric window function by mirroring the input window.

        This function creates a symmetric window by appending a reversed copy of
        the input window to itself.

        """

        window_reversed = window[::-1]
        window_symmetric = np.zeros(self.L)
        window_symmetric[:self.L // 2] = window
        window_symmetric[self.L // 2:] = window_reversed

        return window_symmetric
    
    def calculate_PL(self, window):
        """
        Calculates the processing loss (PL) of a given window. Eq.(8)

        Args:
            window

        Returns:
            The processing loss of the window.
        """
        numerator = np.abs(np.sum(window)) ** 2
        denominator = self.L * np.sum(window ** 2)
        PL = 10 * np.log10(numerator / denominator)

        return PL
    
    def calculate_response(self, window):
        """
        Computes the frequency response of the given window.

        Args:
            window

        Returns:
            frequencies_pi: Normalized frequency values.
            response: Magnitude response in dB.
        """
        frequencies, response = freqz(window, self.freqResolution)
        response = 20 * np.log10(np.abs(response) / np.max(np.abs(response)))
        frequencies_pi = frequencies / (2 * np.pi)

        return frequencies_pi, response
    
    def calculate_pslr(self, window):
        """
        Calculates the Peak Side-Lobe Ratio (PSLR) for a given window function.

        PSLR is a measure of the relative strength of the highest side-lobe
        compared to the main lobe in the response of the given window function.

        Parameters:
            window

        Returns:
            - response[peaks] : array
            The values of the response at the detected peak locations.
            - pslr : float
            The highest peak side-lobe ratio.
        """
        _, response = self.calculate_response(window)
        peaks, _ = find_peaks(response)
        pslr = np.max(response[peaks])
        return response[peaks], pslr
    
    def calculate_mw(self, window):
        """
        Calculates the mean width (MW) of the mainlobe at a given threshold.

        Process:
            1. Computes the frequency response of the given window using `calculate_response(window)`.
            2. Identifies the indices where the magnitude response (in dB) is above `threshold_dB`.
            3. The width of the mainlobe is determined as the count of these indices.
            4. If the identified points are sufficient (more than 1), it returns the number of samples within the mainlobe.
            Otherwise, an error message is printed, and a value of 0 is returned.

        Args:
            window: The window function.

        Returns:
            Mean width of the mainlobe or 0 in case of an error.
        """
        _, response = self.calculate_response(window)
        points = np.where(response >= threshold_dB)[0]
        mean_width = len(points)
        if len(points) > 1:
            return mean_width
        else:
            print("Error in calculate_mw")
            return 0
        
    def objective(self, window):
        """
        Computes the objective function value for a given window.

        The goal is to minimize the Peak Sidelobe Level Ratio (PSLR) while ensuring
        the mainlobe width (MW) remains close to its reference values.
        The objective function is defined as:

            objective = -PSLR - penalty_terms

        Where:
        - `PSLR`: Peak Sidelobe Level Ratio of the given window.
        - `PL`: processing loss of the window.
        - `MW`: Mainlobe width (number of samples in the mainlobe).
        - `MW_rec`: Mainlobe width of the rectangular window (reference).
        - `MW_original`: Mainlobe width of the standard Kaiser window.
        - `pl_original`: Reference processing loss.

        **Penalty Terms:**
        - If any sidelobe peak exceeds the first sidelobe peak, a penalty is applied.
        - If MW deviates significantly from its reference ratio, a penalty is applied.
        - If PL deviates below the reference threshold, a penalty is applied.

        The function returns a negative value because the optimization algorithm
        is designed to maximize the objective, while our goal is to minimize PSLR
        and maintain MW and PL within acceptable limits.

        Args:
            window

        Returns:
            float: The negative objective function value.
        """

        window = self.symmetric_window(window)
        peaks, pslr = self.calculate_pslr(window)
        mw = self.calculate_mw(window)

        objective = - pslr

        if mw / self.mw_rec > self.mw / self.mw_rec:
            objective -= self.lamda * abs(mw / self.mw_rec - self.mw / self.mw_rec)

        return objective
    
    def initialize_fireflies(self, window):
        """
        Initializes a population of fireflies for the Firefly Algorithm.  Eq.(2)

        The function generates `n` fireflies, each represented as a symmetric window function
        of length `L`. The first half of each firefly is based on the standard Kaiser window
        with added random perturbations, and the second half is created by mirroring the first half.
        The fireflies are then normalized to ensure values remain within a valid range.

        Process:
        1. Creates a zero matrix of shape `(n, L)`, where each row represents a firefly (candidate solution).
        2. Generates the first half of the firefly by taking the first half of `window_standard`
        and adding random noise from a uniform distribution between [0,1].
        3. The second half is created as a mirror image of the first half to maintain symmetry.
        4. Stores the generated values in the corresponding firefly's row.
        5. Normalizes each firefly by dividing it by its maximum value to scale between 0 and 1.

        Args:
            L (int): Length of each firefly (window function length).
            n (int): Number of fireflies (population size).

        Returns:
            matrix where each row represents an initialized firefly.
        """
        fireflies = np.zeros((self.n_pop, self.L // 2))

        for k in range(self.n_pop):
            fireflies[k] = window[:self.L // 2] + np.random.uniform(0, 1, self.L // 2)
            fireflies[k] /= np.max(fireflies[k])

        return fireflies
    
    def new_alpha(self, alpha):
        """
        Updates the alpha parameter using an exponential decay formula.

        This function applies a decay factor to the given alpha value, reducing it
        iteratively based on the total number of iterations. The decay is designed
        to gradually decrease alpha over the course of the iterations.

        Parameters:
        alpha :
            The initial value of the alpha parameter.
        max_iter :
            The total number of iterations over which alpha will decay.

        Returns:
            The updated alpha value after applying the decay factor.
        """
        delta = 1 - (1 / 200) ** (1 / self.max_iter)
        alpha *= (1 - delta)

        return alpha
    
    
    def optimizer(self):
        """
        Implements the Firefly Algorithm for window optimization.

        Args:
            lb: Lower bound of window coefficients.
            ub: Upper bound of window coefficients.
            L: Length of the window.
            n_pop: Population size.
            max_iter: Number of iterations.
            alpha: Randomization parameter.
            beta: Attraction coefficient.
            gamma: Light absorption coefficient.

        Returns:
            The optimized window function.
        """
        self.Thread.progress.emit(0)
        population = self.initialize_fireflies(self.window)
        fitness = np.array([self.objective(ind) for ind in population])
        alpha = self.alpha

        for t in range(self.max_iter):
            if self.Thread._is_running:
                for i in range(self.n_pop):
                    for j in range(self.n_pop):
                        if fitness[j] > fitness[i]:
                            r = np.linalg.norm(population[i] - population[j])  # Eq.(6)
                            attraction = self.beta * np.exp(- self.gamma * r ** 2)  # Eq.(5)
                            population[i] += attraction * (population[j] - population[i]) + alpha * (
                                        np.random.uniform(0, 1, self.L // 2) - 0.5)  # Eq.(7)
                            population[i] = np.clip(population[i], 0, 1)
                            fitness[i] = self.objective(population[i])
            else:
                return self.window, self.window
            alpha = self.new_alpha(alpha)
            self.Thread.progress.emit(round(((t + 1) / self.max_iter) * 100, 2))
        
        best_index = np.argmax(fitness)
        self.window_optimized = population[best_index]
        return self.window, self.symmetric_window(self.window_optimized)
    
    def calculate_MW_PSLR_PL(self, window):

        mw = self.calculate_mw(window)
        _, pslr = self.calculate_pslr(window)
        pl = self.calculate_PL(window)
        return round(mw/self.mw_rec, 2), round(pslr, 2), round(pl, 2)

    def calculate_H(self, window):

            freq, H = self.calculate_response(window)
            H = np.clip(H, -60, 0)

            return freq, H
    



