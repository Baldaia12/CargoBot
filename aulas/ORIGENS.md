# Código e recursos reutilizados das aulas

Estes ficheiros acompanham o projeto para que este não dependa do workspace das aulas. As dependências de sistema, como ROS 2 e Gazebo, devem ser instaladas separadamente.

- `simul_worlds/`: subconjunto da Aula 2, repositório
  https://github.com/ruipaulorocha/simul_worlds.
  Inclui gazebo.launch.py, building.sdf, GUI e malha do edifício.
  CMake/package.xml foram reduzidos aos recursos utilizados. A luz Sun do Fuel foi
  substituída por uma luz embutida equivalente para evitar downloads no arranque.
- `turtlebot4*`, `irobot/`, `LICENSE`, `README.md`: cópia do simulador disponibilizado
  nas aulas, https://github.com/ruipaulorocha/turtlebot4. Fontes, modelos, mensagens e licenças
  incluídos; diretórios Git e ficheiros gerados não foram copiados.
- `explore_lite/`: exploração por fronteiras disponibilizada na Aula 6,
  https://github.com/ruipaulorocha/m-explore-ros2.
  Em src/explore.cpp foram corrigidos dois casos: reenvio após pausa e seleção
  imediata de outra fronteira após sucesso (em vez de esperar pelo timeout).
- `referencias_aula6/`: exemplos de consulta de cr_slam/cr_amcl, não executados.
  A integração nova preserva SLAM Toolbox em vez do GMapping do exemplo autónomo.

`src/trc_mapping/config/nav2.yaml` foi adaptado de
`aulas/turtlebot4_navigation/config/nav2.yaml`: velocidades reduzidas, raio oficial 0.175 m,
LiDAR absoluto /scan e CostCritic configurado para footprint circular.
`explore.yaml` deriva do explore.yaml da Aula 6, com tópicos /map e /map_updates
consistentes e timeout de progresso maior. O launch autónomo e a verificação de
prontidão são integração nova do trabalho.

A costmap local usa apenas LiDAR 2D e inflação, sem a camada estática do mapa em
construção: evita paredes antigas junto do robô quando o SLAM corrige o mapa.
Mantém-se MPPI, como nas aulas. A costmap global continua a usar o mapa do SLAM.
