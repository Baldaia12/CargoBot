# CargoBot — mapeamento manual e exploração autónoma

ROS 2 Jazzy / Ubuntu 24.04 / Gazebo Harmonic. Todos os pacotes e recursos das aulas
usados na execução estão em `aulas/`.
As bibliotecas e ferramentas de sistema são dependentes de de instalação.
As origens e modificações estão em `aulas/ORIGENS.md`.

## Instalar dependências num computador novo

Instalar ROS 2 Jazzy desktop pelos procedimentos oficiais. Instalar ferramentas:

```bash
sudo apt update
sudo apt install python3-colcon-common-extensions python3-rosdep ros-jazzy-ros-gz ros-jazzy-navigation2 ros-jazzy-nav2-bringup ros-jazzy-slam-toolbox ros-jazzy-teleop-twist-keyboard ros-jazzy-gz-ros2-control
```

Se rosdep nunca foi inicializado: `sudo rosdep init`. Depois, na raiz do projeto:

```bash
source /opt/ros/jazzy/setup.bash
rosdep update
rosdep install --from-paths src aulas --ignore-src -r -y --rosdistro jazzy
colcon build --symlink-install --parallel-workers 3 --cmake-args -DBUILD_TESTING=OFF -DCMAKE_BUILD_TYPE=Release
```

Usar um terminal novo, sem ter carregado outros workspaces. O colcon descobre os
pacotes de `src/` e `aulas/` recursivamente. Não limitar a primeira compilação a
`--packages-select trc_mapping`: também é preciso construir os pacotes incluídos.
`build/`, `install/` e `log/` são gerados localmente e não devem ser enviados ao Git.
Ao mudar a pasta do projeto, recompilar sem reutilizar estas três pastas antigas.

## Requisito 1 — mapeamento manual

Na raiz do projeto:

```bash
source ambiente.bash
ros2 launch trc_mapping manual.launch.py
```

Noutro terminal na mesma pasta:

```bash
source ambiente.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true -p use_sim_time:=true -p speed:=0.2
```

`i` avança, `j/l` rodam, `k` para. Manter foco no terminal. O controlador trava se
deixar de receber comandos. Percorrer corredores e salas e revisitar áreas antigas.
O mapa existente `maps/cargobot_final.*` foi criado manualmente pelo aluno e é preservado.

## Requisito 2 — exploração autónoma

Fechar a execução manual antes de iniciar a autónoma. Num terminal novo:

```bash
source ambiente.bash
ros2 launch trc_mapping autonomous_mapping.launch.py
```

Não iniciar teleop simultaneamente. Esta execução começa com um mapa novo:
não carrega o mapa manual. SLAM Toolbox constrói o mapa; explore_lite seleciona
fronteiras; Nav2 planeia e conduz; velocity_smoother e collision_monitor tratam os
comandos. O explorador só arranca com mapa, TF e todos os servidores ativos.
RViz mostra mapa, robô, LiDAR, fronteiras e caminho planeado.

Pausar a exploração (noutro terminal com source ambiente.bash):

```bash
ros2 topic pub --once /explore/resume std_msgs/msg/Bool '{data: false}'
```

Retomar: repetir com `data: true`. Ao acabar as fronteiras que consegue explorar,
o explorador tenta regressar à posição inicial. Isso não prova cobertura total:
fronteiras impossíveis ou sem progresso podem ser excluídas. Inspecionar o mapa
e os logs antes de considerar o ensaio completo.

## Guardar mapa (qualquer modo)

Manter a simulação aberta. Na raiz, noutro terminal:

```bash
source ambiente.bash
ros2 run nav2_map_server map_saver_cli -f "maps/cargobot_$(date +%Y%m%d_%H%M%S)" --ros-args -p use_sim_time:=true -p save_map_timeout:=15.0
```

Guardar YAML e PGM juntos. O nome datado evita sobrescrever mapas anteriores.
Terminar com Ctrl+C no teleop, se existir, e depois no launch.

## Verificar

```bash
source ambiente.bash
ros2 lifecycle get /slam_toolbox
ros2 topic echo /map --once --field header
python3 tests/observe.py 60
```

No modo autónomo verificar também `ros2 lifecycle get /bt_navigator`.
O observador verifica mensagens, TF, movimento, objetivos Nav2 e crescimento do
mapa. Não envia comandos. Um objetivo Nav2 com estado 4 terminou com sucesso.

`ambiente.bash` escolhe Fast DDS normal, domínio ROS 42 e partição Gazebo própria.
Não usa perfil DDS XML personalizado. Todos os terminais devem carregar o mesmo
ambiente. Para ensaios isolados: `export TRC_DOMAIN_ID=46` antes do source.
