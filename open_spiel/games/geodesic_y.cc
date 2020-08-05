// Copyright 2019 DeepMind Technologies Ltd. All rights reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "open_spiel/games/geodesic_y.h"

#include <algorithm>
#include <memory>
#include <utility>
#include <vector>

#include "open_spiel/game_parameters.h"
#include "open_spiel/utils/tensor_view.h"

namespace open_spiel {
namespace geodesic_y_game {
namespace {

// Facts about the game.
const GameType kGameType{/*short_name=*/"geodesic_y",
                         /*long_name=*/"Geodesic Y Connection Game",
                         GameType::Dynamics::kSequential,
                         GameType::ChanceMode::kDeterministic,
                         GameType::Information::kPerfectInformation,
                         GameType::Utility::kZeroSum,
                         GameType::RewardModel::kTerminal,
                         /*max_num_players=*/2,
                         /*min_num_players=*/2,
                         /*provides_information_state_string=*/true,
                         /*provides_information_state_tensor=*/false,
                         /*provides_observation_string=*/true,
                         /*provides_observation_tensor=*/true,
                         /*parameter_specification=*/
                         {
                             {"board_size", GameParameter(kDefaultBoardSize)},
                             {"ansi_color_output", GameParameter(false)},
                         }};

std::shared_ptr<const Game> Factory(const GameParameters& params) {
  return std::shared_ptr<const Game>(new GeodesicYGame(params));
}

REGISTER_SPIEL_GAME(kGameType, Factory);

// The board is represented as a flattened 2d array of the form:
//   1 2 3
// A 0 1 2     0 1 2     0 1 2
// B 3 4 5 <=> 3 4   <=>  3 4
// C 6 7 8     6           6
//
// Neighbors are laid out in this pattern:
//   0   1           0  1
// 5   X   2 <=>  5  X  2
//   4   3        4  3

// Direct neighbors of a cell, clockwise.
/*
constexpr std::array<Move, kMaxNeighbors> neighbor_offsets = {
    Move(0, -1, kMoveOffset), Move(1, -1, kMoveOffset),
    Move(1, 0, kMoveOffset),  Move(0, 1, kMoveOffset),
    Move(-1, 1, kMoveOffset), Move(-1, 0, kMoveOffset),
};
*/

// Precomputed list of neighbors per board_size: [board_size][cell][direction]
// std::vector<NeighborList> neighbor_list;
NeighborList neighbor_list;

NeighborList geodesic_graph(int board_size) {
  if (board_size < 2) {
        throw std::runtime_error("bruh");
    }

  int v = 0;
  NeighborList graph(3 * ((board_size - 1) * (board_size - 1) + (board_size - 1)) / 2);

  std::vector<uint16_t> right, bottom, left;
  std::vector<uint16_t> b_right, b_bottom, b_left;

  auto join = [&] (uint16_t v1, uint16_t v2) {
      graph[v1].push_back(v2);
      graph[v2].push_back(v1);
  };

  for (int i = 1; i < board_size; i++) {
      b_right.swap(right);
      b_bottom.swap(bottom);
      b_left.swap(left);

      right.clear();
      bottom.clear();
      left.clear();

      right.shrink_to_fit();
      bottom.shrink_to_fit();
      left.shrink_to_fit();

      for (int j = 0; j < i; j++) {
          right.push_back(v++);
          if (j > 0) {
              join(v - 1, v - 2);
          }
      }
      for (int j = 0; j < i; j++) {
          bottom.push_back(v++);
          if (j > 0) {
              join(v - 1, v - 2);
          }
      }
      for (int j = 0; j < i; j++) {
          left.push_back(v++);
          if (j > 0) {
              join(v - 1, v - 2);
          }
      }

      join(right[0], left[left.size() - 1]);
      join(bottom[0], right[right.size() - 1]);
      join(left[0], bottom[bottom.size() - 1]);

      if (b_right.size() > 0) {
          join(right[0], b_right[0]);
          for (size_t j = 1; j < (right.size() - 1); j++) {
              join(right[j], b_right[j - 1]);
              join(right[j], b_right[j]);
          }
          join(right[right.size() - 1], b_right[b_right.size() - 1]);
          join(right[right.size() - 1], b_bottom[0]);
      }
      if (b_bottom.size() > 0) {
          join(bottom[0], b_bottom[0]);
          for (size_t j = 1; j < (bottom.size() - 1); j++) {
              join(bottom[j], b_bottom[j - 1]);
              join(bottom[j], b_bottom[j]);
          }
          join(bottom[bottom.size() - 1], b_bottom[b_bottom.size() - 1]);
          join(bottom[bottom.size() - 1], b_left[0]);
      }
      if (b_left.size() > 0) {
          join(left[0], b_left[0]);
          for (size_t j = 1; j < (left.size() - 1); j++) {
              join(left[j], b_left[j - 1]);
              join(left[j], b_left[j]);
          }
          join(left[left.size() - 1], b_left[b_left.size() - 1]);
          join(left[left.size() - 1], b_right[0]);
      }
  }

  std::vector<uint16_t> graph_left(left);
  std::vector<uint16_t> graph_bottom(bottom);
  std::vector<uint16_t> graph_right(right);

  graph_left.push_back(graph_right[0]);
  graph_bottom.push_back(graph_left[0]);
  graph_right.push_back(graph_bottom[0]);

  graph.push_back(graph_right);
  graph.push_back(graph_bottom);
  graph.push_back(graph_left);

  return graph;
}

/*
const NeighborList& get_neighbors(int board_size) {
  if (board_size >= neighbor_list.size()) {
    neighbor_list.resize(board_size + 1);
  }
  if (neighbor_list[board_size].empty()) {
    neighbor_list[board_size] = gen_neighbors(board_size);
  }
  return neighbor_list[board_size];
}
*/

}  // namespace

/*
int Move::Edge(int board_size) const {
  if (!OnBoard()) return 0;

  return (x == 0 ? (1 << 0) : 0) | (y == 0 ? (1 << 1) : 0) |
         (x + y == board_size - 1 ? (1 << 2) : 0);
}

std::string Move::ToString() const {
  if (xy == kMoveUnknown) return "unknown";
  if (xy == kMoveNone) return "none";
  return absl::StrCat(std::string(1, static_cast<char>('a' + x)), y + 1);
}
*/

GeodesicYState::GeodesicYState(std::shared_ptr<const Game> game, uint16_t board_size, bool ansi_color_output)
    : State(game),
      graph(geodesic_graph(board_size)),
      board_size_(3 * ((board_size - 1) * (board_size - 1) + (board_size - 1)) / 2),
      ansi_color_output_(ansi_color_output) {
  board_.resize(board_size_);
  graph_left   = graph.back();
  graph.pop_back();
  graph_bottom = graph.back();
  graph.pop_back();
  graph_right  = graph.back();
  graph.pop_back();
  for (uint16_t i = 0; i < board_size_; i++) {
    uint8_t edge = 0;
    for (size_t j = 0; j < graph_left.size(); j++) {
      if (i == graph_left[j]) {
        edge |= 0b1;
      }
    }
    for (size_t j = 0; j < graph_bottom.size(); j++) {
      if (i == graph_bottom[j]) {
        edge |= 0b10;
      }
    }
    for (size_t j = 0; j < graph_right.size(); j++) {
      if (i == graph_right[j]) {
        edge |= 0b100;
      }
    }
    board_[i] = Cell(kPlayerNone, i, edge);
  }
}

/*
Move GeodesicYState::ActionToMove(Action action_id) const {
  return Move(action_id % board_size_, action_id / board_size_, board_size_);
}
*/

std::vector<Action> GeodesicYState::LegalActions() const {
  // Can move in any empty cell.
  std::vector<Action> moves;
  if (IsTerminal()) return moves;
  moves.reserve(board_size_ - moves_made_);
  for (uint16_t cell = 0; cell < board_size_; cell++) {
    if (board_[cell].player == kPlayerNone) {
      moves.push_back(cell);
    }
  }
  return moves;
}

std::string GeodesicYState::ActionToString(Player player, Action action_id) const {
  return std::to_string(action_id); // fix dis
}

/*
std::string GeodesicYState::ToString() const {
  // Generates something like:
  //  a b c d e f g h i j k
  // 1 O @ O O . @ @ O O @ O
  //  2 . O O . O @ @ . O O
  //   3 . O @ @ O @ O O @
  //    4 O O . @ . @ O O
  //     5 . . . @[@]@ O
  //      6 @ @ @ O O @
  //       7 @ . O @ O
  //        8 . @ @ O
  //         9 @ @ .
  //         10 O .
  //          11 @

  std::string white = "O";
  std::string black = "@";
  std::string empty = ".";
  std::string coord = "";
  std::string reset = "";
  if (ansi_color_output_) {
    std::string esc = "\033";
    reset = esc + "[0m";
    coord = esc + "[1;37m";  // bright white
    empty = reset + ".";
    white = esc + "[1;33m" + "@";  // bright yellow
    black = esc + "[1;34m" + "@";  // bright blue
  }

  std::ostringstream out;

  // Top x coords.
  out << ' ';
  for (int x = 0; x < board_size_; x++) {
    out << ' ' << coord << static_cast<char>('a' + x);
  }
  out << '\n';

  for (int y = 0; y < board_size_; y++) {
    out << std::string(y + ((y + 1) < 10), ' ');  // Leading space.
    out << coord << (y + 1);                      // Leading y coord.

    bool found_last = false;
    for (int x = 0; x < board_size_ - y; x++) {
      Move pos(x, y, board_size_);

      // Spacing and last-move highlight.
      if (found_last) {
        out << coord << ']';
        found_last = false;
      } else if (last_move_ == pos) {
        out << coord << '[';
        found_last = true;
      } else {
        out << ' ';
      }

      // Actual piece.
      Player p = board_[pos.xy].player;
      if (p == kPlayerNone) out << empty;
      if (p == kPlayer1) out << white;
      if (p == kPlayer2) out << black;
    }
    if (found_last) {
      out << coord << ']';
    }
    out << '\n';
  }
  out << reset;
  return out.str();
}
*/
std::string GeodesicYState::ToString() const {
  std::string white = "O";
  std::string black = "@";
  std::string empty = ".";
  std::string reset = "";
  if (ansi_color_output_) {
    std::string esc = "\033";
    reset = esc + "[0m";
    empty = reset + ".";
    white = esc + "[1;33m" + "@";  // bright yellow
    black = esc + "[1;34m" + "@";  // bright blue
  }
  std::ostringstream out;
  for (uint16_t i = 0; i < board_size_; i++) {
    if (board_[i].player == kPlayer1) {
      out << white;
    }
    else if (board_[i].player == kPlayer2) {
      out << black;
    }
    else {
      out << empty;
    }
  }
  out << '\n';
  out << reset;
  return out.str();
}

std::vector<double> GeodesicYState::Returns() const {
  if (outcome_ == kPlayer1) return {1, -1};
  if (outcome_ == kPlayer2) return {-1, 1};
  return {0, 0};  // Unfinished
}

std::string GeodesicYState::InformationStateString(Player player) const {
  SPIEL_CHECK_GE(player, 0);
  SPIEL_CHECK_LT(player, num_players_);
  return HistoryString();
}

std::string GeodesicYState::ObservationString(Player player) const {
  SPIEL_CHECK_GE(player, 0);
  SPIEL_CHECK_LT(player, num_players_);
  return ToString();
}

int PlayerRelative(GeodesicYPlayer state, Player current) {
  switch (state) {
    case kPlayer1:
      return (current == 0) ? 0 : 1;
    case kPlayer2:
      return (current == 1) ? 0 : 1;
    case kPlayerNone:
      return 2;
    default:
      SpielFatalError("Unknown player type.");
  }
}

void GeodesicYState::ObservationTensor(Player player,
                               std::vector<double>* values) const {
  SPIEL_CHECK_GE(player, 0);
  SPIEL_CHECK_LT(player, num_players_);

  TensorView<2> view(values, {kCellStates, static_cast<int>(board_size_)}, true);
  for (int i = 0; i < board_size_; ++i) {
    view[{PlayerRelative(board_[i].player, player), i}] = 1.0;
  }
}
/*
void GeodesicYState::DoApplyAction(Action action) {
  SPIEL_CHECK_EQ(board_[action].player, kPlayerNone);
  SPIEL_CHECK_EQ(outcome_, kPlayerNone);

  Move move = ActionToMove(action);
  SPIEL_CHECK_TRUE(move.OnBoard());

  last_move_ = move;
  board_[move.xy].player = current_player_;
  moves_made_++;

  for (const Move& m : neighbors[move.xy]) {
    if (m.OnBoard() && current_player_ == board_[m.xy].player) {
      JoinGroups(move.xy, m.xy);
    }
  }

  if (board_[FindGroupLeader(move.xy)].edge == 0x7) {  // ie all 3 edges.
    outcome_ = current_player_;
  }

  current_player_ = (current_player_ == kPlayer1 ? kPlayer2 : kPlayer1);
}
*/
void GeodesicYState::DoApplyAction(Action action) {
  SPIEL_CHECK_EQ(board_[action].player, kPlayerNone);
  SPIEL_CHECK_EQ(outcome_, kPlayerNone);

  moves_made_++;
  board_[action].player = current_player_;

  for (size_t i = 0; i < graph[action].size(); i++) {
    if (board_[graph[action][i]].player == current_player_) {
       JoinGroups(action, graph[action][i]);
    }
  }
  uint16_t leader = FindGroupLeader(action);
  //board_[leader].edge |= board_[action].edge;
  if ((board_[leader].edge & 0b111) == 0b111) {
    outcome_ = current_player_;
  }
  current_player_ = (current_player_ == kPlayer1 ? kPlayer2 : kPlayer1);
}

int GeodesicYState::FindGroupLeader(int cell) {
  uint16_t parent = board_[cell].parent;
  if (parent != cell) {
    do {  // Follow the parent chain up to the group leader.
      parent = board_[parent].parent;
    } while (parent != board_[parent].parent);
    // Do path compression, but only the current one to avoid recursion.
    board_[cell].parent = parent;
  }
  return parent;
}

bool GeodesicYState::JoinGroups(int cell_a, int cell_b) {
  uint16_t leader_a = FindGroupLeader(cell_a);
  uint16_t leader_b = FindGroupLeader(cell_b);

  if (leader_a == leader_b)  // Already the same group.
    return true;

  if (board_[leader_a].size < board_[leader_b].size) {
    // Force group a's subtree to be bigger.
    std::swap(leader_a, leader_b);
  }

  // Group b joins group a.
  board_[leader_b].parent = leader_a;
  board_[leader_a].size += board_[leader_b].size;
  board_[leader_a].edge |= board_[leader_b].edge;

  return false;
}

std::unique_ptr<State> GeodesicYState::Clone() const {
  return std::unique_ptr<State>(new GeodesicYState(*this));
}

GeodesicYGame::GeodesicYGame(const GameParameters& params)
    : Game(kGameType, params),
      board_size_(ParameterValue<int>("board_size")),
      ansi_color_output_(ParameterValue<bool>("ansi_color_output")) {}

}  // namespace geodesic_y_game
}  // namespace open_spiel
