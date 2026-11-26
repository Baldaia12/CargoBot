#!/usr/bin/env python3
"""Inicia a exploração quando o SLAM e o Nav2 estiverem prontos."""

import os
from pathlib import Path
import time

from ament_index_python.packages import (
    get_package_prefix,
    get_package_share_directory,
)
from lifecycle_msgs.srv import GetState
from nav_msgs.msg import OccupancyGrid
import rclpy
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from tf2_ros import Buffer, TransformListener


def main():
    rclpy.init()
    node = rclpy.create_node('exploration_readiness')

    # Guarda se já recebemos um mapa com dados.
    # A lista permite que a função callback atualize este valor.
    received = [False]

    # Transient Local permite receber o último mapa mesmo que tenha sido
    # publicado antes do arranque deste nó.
    qos = QoSProfile(
        depth=1,
        durability=DurabilityPolicy.TRANSIENT_LOCAL,
        reliability=ReliabilityPolicy.RELIABLE,
    )

    subscription = node.create_subscription(
        OccupancyGrid,
        '/map',
        lambda msg: received.__setitem__(0, bool(msg.data)),
        qos,
    )

    # O listener recebe as transformações TF e guarda-as no buffer.
    buffer = Buffer()
    listener = TransformListener(buffer, node)

    # Todos estes nós devem estar no estado "active" antes de explorar.
    names = [
        'slam_toolbox',
        'controller_server',
        'planner_server',
        'smoother_server',
        'behavior_server',
        'bt_navigator',
        'velocity_smoother',
        'collision_monitor',
    ]

    clients = {
        name: node.create_client(GetState, f'/{name}/get_state')
        for name in names
    }

    node.get_logger().info(
        'A aguardar mapa, TF e todos os servidores Nav2 ativos.'
    )

    # Usa tempo real para limitar a espera, mesmo com a simulação parada.
    deadline = time.monotonic() + 240

    while rclpy.ok() and time.monotonic() < deadline:
        # Processa mensagens e callbacks recebidos pelo nó.
        rclpy.spin_once(node, timeout_sec=0.2)

        # Só verifica os servidores depois de existir mapa e uma ligação
        # TF disponível entre o referencial do mapa e o robô.
        if not received[0] or not buffer.can_transform(
            'map', 'base_link', rclpy.time.Time()
        ):
            continue

        ready = True

        for client in clients.values():
            if not client.service_is_ready():
                ready = False
                break

            # Pede o estado do nó sem bloquear indefinidamente.
            future = client.call_async(GetState.Request())
            rclpy.spin_until_future_complete(
                node, future, timeout_sec=1.0
            )

            # O identificador 3 corresponde ao estado lifecycle "active".
            if (
                not future.done()
                or future.result() is None
                or future.result().current_state.id != 3
            ):
                ready = False
                break

        if ready:
            node.get_logger().info(
                'SLAM e Nav2 prontos. A iniciar exploração autónoma.'
            )

            # A verificação terminou; este nó já não é necessário.
            node.destroy_node()
            rclpy.shutdown()

            executable = str(
                Path(get_package_prefix('explore_lite'))
                / 'lib/explore_lite/explore'
            )

            params = str(
                Path(get_package_share_directory('trc_mapping'))
                / 'config/explore.yaml'
            )

            # Substitui este processo pelo explorador, com a configuração
            # do projeto e o relógio da simulação.
            os.execv(
                executable,
                [
                    executable,
                    '--ros-args',
                    '-r', '__node:=explore',
                    '--params-file', params,
                    '-p', 'use_sim_time:=true',
                ],
            )

    # Se o sistema não ficar pronto, termina com código de erro.
    node.get_logger().error(
        'Arranque cancelado: SLAM/Nav2 não ficaram prontos em 240 s.'
    )

    node.destroy_node()
    rclpy.shutdown()
    raise SystemExit(1)


if __name__ == '__main__':
    main()
