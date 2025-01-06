import numpy as np

class KDNode:
    def __init__(self, point, index, axis, left=None, right=None):
        self.point = point   # ノードの点
        self.index = index   # 元の配列におけるインデックス
        self.axis = axis     # 分割軸
        self.left = left     # 左の子ノード
        self.right = right   # 右の子ノード

class KDTree:
    def __init__(self, points):
        # 点とそのインデックスを保持
        indexed_points = [(point, idx) for idx, point in enumerate(points)]
        self.root = self.build_kdtree(indexed_points, axis=0)

    def build_kdtree(self, indexed_points, axis):
        if not indexed_points:
            return None
        # ソートし、中央値を取得
        indexed_points.sort(key=lambda x: x[0][axis])
        median_idx = len(indexed_points) // 2
        # 次の分割軸
        next_axis = (axis + 1) % 2
        return KDNode(
            point=indexed_points[median_idx][0],
            index=indexed_points[median_idx][1],
            axis=axis,
            left=self.build_kdtree(indexed_points[:median_idx], next_axis),
            right=self.build_kdtree(indexed_points[median_idx+1:], next_axis)
        )

    def find_k_nearest(self, query_point, k):
        best_points = []
        self.search_k_nearest(self.root, query_point, k, best_points)
        # 距離でソートし、最初のk個のインデックスを取得
        return [x[1] for x in sorted(best_points, key=lambda x: x[0])][:k]

    def search_k_nearest(self, node, query_point, k, best_points):
        if node is None:
            return
        # 点との距離を計算
        dist = np.sum((np.array(query_point) - np.array(node.point))**2)
        # リストがフルでない場合、または現在の点が既存の点より近い場合
        if len(best_points) < k or dist < best_points[-1][0]:
            if len(best_points) >= k:
                best_points.pop()  # 最も遠い点を削除
            best_points.append((dist, node.index))
            best_points.sort(key=lambda x: x[0])  # ソート
        # 再帰的に探索
        next_axis = (node.axis + 1) % 2
        if query_point[node.axis] < node.point[node.axis]:
            self.search_k_nearest(node.left, query_point, k, best_points)
            if len(best_points) < k or (query_point[node.axis] - node.point[node.axis])**2 < best_points[-1][0]:
                self.search_k_nearest(node.right, query_point, k, best_points)
        else:
            self.search_k_nearest(node.right, query_point, k, best_points)
            if len(best_points) < k or (query_point[node.axis] - node.point[node.axis])**2 < best_points[-1][0]:
                self.search_k_nearest(node.left, query_point, k, best_points)