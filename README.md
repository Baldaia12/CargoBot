# CargoBot · mapeamento manual

O operador conduz um TurtleBot 4 no edifício das aulas em Gazebo Harmonic. O SLAM Toolbox combina o laser 2D com as transformações do robô e publica uma grelha de ocupação com resolução de 5 cm. O RViz mostra o modelo, o laser e o mapa em construção.

## Preparar e arrancar

Usar Bash, Ubuntu 24.04, ROS 2 Jazzy e o workspace compilado das aulas 2 e 6 (incluindo simul_worlds e o TurtleBot 4 das aulas). As outras dependências de execução estão em src/trc_mapping/package.xml. Se o workspace das aulas estiver noutro computador ou pasta, definir TRC_AULAS_WS com o caminho absoluto desse workspace antes de carregar o ambiente. Compilar uma vez após copiar o projeto.

```bash
cd /home/baldaia/Documents/RC/TRC
source ambiente.bash
colcon build --symlink-install --packages-select trc_mapping
source ambiente.bash
ros2 launch trc_mapping manual.launch.py
```

Usar uma execução do launch de cada vez. O ficheiro ambiente.bash configura o domínio ROS 42, a partição Gazebo do projeto e um perfil Fast DDS para comunicação entre os processos neste computador.

## Conduzir e guardar

Num segundo terminal:

```bash
cd /home/baldaia/Documents/RC/TRC
source ambiente.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true -p use_sim_time:=true -p speed:=0.2
```

Com o foco no terminal do teclado, manter `i` premido para avançar, usar `j` e `l` para rodar e `k` para parar. O controlador trava se deixar de receber comandos. Percorrer as salas e os corredores e voltar a passar por uma zona já mapeada. No RViz, o espaço livre aparece claro, as paredes escuras e as áreas desconhecidas cinzentas.

Quando a cobertura for suficiente, parar com `k`, manter a simulação aberta e guardar num terceiro terminal. Cada execução deste bloco cria um prefixo datado.

```bash
cd /home/baldaia/Documents/RC/TRC
source ambiente.bash
ros2 run nav2_map_server map_saver_cli -f "maps/cargobot_$(date +%Y%m%d_%H%M%S)" --ros-args -p use_sim_time:=true -p save_map_timeout:=15.0
```

Guardar juntos o YAML e a imagem PGM. O par `maps/ensaio_manual.*` é uma amostra obtida ao conduzir o robô numa parte do edifício. Para fechar uma sessão iniciada por ti, usar Ctrl+C primeiro no teclado e depois no terminal do launch.

## Verificação rápida

Com o mesmo ambiente e a simulação em execução:

```bash
ros2 service call /slam_toolbox/get_state lifecycle_msgs/srv/GetState '{}'
ros2 run tf2_ros tf2_echo map base_link
```

O serviço deve responder `active`. A segunda ferramenta imprime a pose do robô e termina com Ctrl+C. Para confirmar o resultado visual, verificar que o robô se desloca no RViz e que o mapa revela novas áreas.

## Referências usadas

- Aula 2, simul_worlds: launch/gazebo.launch.py, gazebo_worlds/building.sdf e a pose inicial em worlds/1pioneer_building.world. O launch deste projeto inclui o mundo e lança uma única instância do robô com a bridge ligada ao mesmo mundo.
- Aula 6, cr_slam: launch/gazebo_slam_toolbox_1turtlebot4_building.launch.py, config/slam.yaml e config/slam.rviz. Serviram de referência para o SLAM síncrono, os frames e os displays. Os ficheiros de integração deste pacote foram escritos para este exercício.
- Aula 8, diapositivo 3: gravação da grelha com nav2_map_server/map_saver_cli.
