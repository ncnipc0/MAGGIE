import numpy as np
from loguru import logger
import difflib
import xml.etree.ElementTree as ET

class KM_Algorithm:
    def __init__(self, datas):
        # weight matrix
        self.matrix = np.array(datas) if not isinstance(datas, np.ndarray) else datas
        # print(self.matrix)
        # Number of left and right nodes in the matrix
        self.row, self.col = self.matrix.shape

        # Adjust to a square array
        self.adj_matrix()

        # Number of left and right nodes
        self.size = self.matrix.shape[0]

        # Initialize Top Label
        self.label_left = np.max(self.matrix, axis=1)  # Initialize the top label and set the left top label to the maximum weight value (maximum value per row)
        self.label_right = np.zeros(self.size)  # Set the top label of the right set to 0

        # Initialize auxiliary variables : whether they have been matched
        self.visit_left = np.zeros(self.size, dtype=bool)
        self.visit_right = np.zeros(self.size, dtype=bool)

        # Initialize the matching result on the right. If it is already matched, it will correspond to the matching result
        self.match_right = np.empty(self.size) * np.nan

        # Record the variable with the minimum value
        self.inc = 999999

        # Record maximum matching sum
        self.sum = self.calculate_sum()

    # Fill the matrix with 0 as a square matrix
    def adj_matrix(self):
        if self.row > self.col:
            self.matrix = np.c_[self.matrix, np.array([[0] * (self.row - self.col)] * self.row)]
        elif self.col > self.row:
            self.matrix = np.r_[self.matrix, np.array([[0] * self.col] * (self.col - self.row))]


    def match(self, boy, depth=0):
        boy = int(boy)
        # Record that this boy has been searched
        self.visit_left[boy] = True
        for girl in range(self.size):
            # If this girl hasn't been matched yet
            if not self.visit_right[girl]:
                gap = self.label_left[boy] + self.label_right[girl] - self.matrix[boy][girl]
                if gap == 0:
                    self.visit_right[girl] = True
                    if np.isnan(self.match_right[girl]) or self.match(self.match_right[girl]):
                        self.match_right[girl] = boy
                        return 1

                # Find the minimum weight difference
                elif self.inc > gap:
                    self.inc = gap
        return 0

    def Kuh_Munkras(self):
        # logger.debug("call Kuh_Munkras")
        self.match_right = np.empty(self.size) * np.nan

        # find the perfect match
        for man in range(self.size):
            count = 0
            while True:
                count += 1
                self.inc = 999999  # the minimum gap
                self.reset()  # Every time a path is searched for, it needs to be reset

                if self.match(man):
                    break
                if count == 300:
                    self.match_right = [0] * self.size
                    break

                for k in range(self.size):
                    if self.visit_left[k]:
                        self.label_left[k] -= self.inc
                for n in range(self.size):
                    if self.visit_right[n]:
                        self.label_right[n] += self.inc

    def calculate_sum(self):
        self.Kuh_Munkras()
        sum = 0
        for i in range(self.size):
            sum += self.matrix[int(self.match_right[i])][i]
        return sum

    def get_match_result(self):
        result_row = [-1] * self.row
        result_col = [-1] * self.col
        for i in range(self.row):
            if int(self.match_right[i]) < self.col:
                result_row[i] = int(self.match_right[i])
                result_col[int(self.match_right[i])] = i

        return result_row, result_col


    def set_Bipartite_Graph(self, Bipartite_Graph):
        self.matrix = Bipartite_Graph

    def reset(self):
        self.visit_left = np.zeros(self.size, dtype=bool)
        self.visit_right = np.zeros(self.size, dtype=bool)


def string_sim(textlist1: list, textlist2: list):
    """
    String similarity
    """
    and_count = len(set(textlist1) & set(textlist2))
    or_count = len(set(textlist1) | set(textlist2))
    if or_count != 0:
        return and_count / or_count
    else:
        return 1


def count_children(root):
    """
    Number of child nodes
    """
    from SenseTree import STElement
    if isinstance(root, ET.Element):
        return len(root)
    elif isinstance(root, STElement):
        return len(root.children)
    else:
        assert "Node type error"


def get_child(root, index):
    from SenseTree import STElement
    if isinstance(root, ET.Element):
        return root[index]
    elif isinstance(root, STElement):
        return root.children[index]
    else:
        assert "Node type error"


def count_old_tree(root: ET.Element):
    count = 1
    for child in root:
        count += count_old_tree(child)
    return count


def count_tree(root) -> int:
    """
    Subtree node count
    """
    from SenseTree import STElement
    if isinstance(root, ET.Element):
        return count_old_tree(root)
    elif isinstance(root, STElement):
        return root.subTreeCount
    else:
        assert "Node type error"


def sim_node(node1, node2, mode: int):
    """
    Node similarity
    """
    sim = 1
    from SenseTree import STElement
    if isinstance(node1, ET.Element) and isinstance(node2, ET.Element):
        if (node1.attrib["class"] != node2.attrib["class"]
                or node1.attrib["checkable"] != node2.attrib["checkable"]
                or node1.attrib["clickable"] != node2.attrib["clickable"]):
            return 0
    elif isinstance(node1, STElement) and isinstance(node2, STElement):
        if node1.node.attrib["class"] != node2.node.attrib["class"] or node1.widget_type != node2.widget_type:
            return 0
    else:
        assert "Node type error"
    return sim


def sim_tree(root1, root2, mode: int):
    """
    Tree similarity
    """
    sim_root = sim_node(root1, root2, mode)
    n1, n2 = count_tree(root1), count_tree(root2)
    if n1 + n2 < 2:
        return 0
    else:
        if sim_root < 0.9:
            return sim_root * 2 / (n1 + n2)
        else:
            opt = 0
            l1, l2 = count_children(root1), count_children(root2)
            if l1 != 0 and l2 != 0:
                w = np.zeros((l1, l2), dtype=float)
                for i in range(0, l1):
                    for j in range(0, l2):
                        w[i][j] = sim_tree(get_child(root1, i), get_child(root2, j), mode)
                best_match_row, best_match_col = KM_Algorithm(w).get_match_result()
                for i in range(0, l1):
                    opt += count_tree(get_child(root1, i)) * w[i][best_match_row[i]] if best_match_row[i] != -1 else 0
                for i in range(0, l2):
                    opt += count_tree(get_child(root2, i)) * w[best_match_col[i]][i] if best_match_col[i] != -1 else 0
            return (sim_root * 2 + opt) / (n1 + n2)




def sim_text(textlist1: list, textlist2: list):
    """
    字符串相似度
    """
    sim = difflib.SequenceMatcher(None, "".join(textlist1), "".join(textlist2)).quick_ratio()
    return sim



def is_same_kind_page(page1, page2, hold=0.7):
    if page1 is None and page2 is None:
        return True
    elif page1 is None or page2 is None:
        return False
    sim = sim_tree(page1.sense_root, page2.sense_root, 1)
    if sim >= hold:
        # logger.debug("structural similarity{} True", sim)
        return True
    else:
        # logger.debug("structural similarity{} False", sim)
        return False


def is_same_page(page1, page2, threshold=0.7):
    if page1 is None and page2 is None:
        return True
    elif page1 is None or page2 is None:
        return False

    sim = 0.5 * sim_tree(page1.sense_root, page2.sense_root, 1) + 0.5 * sim_text(page1.texts, page2.texts)
    if sim >= threshold:
        # logger.debug("content similarity{} True", sim)
        return True
    else:
        # logger.debug("content similarity{} False", sim)
        return False