clear all; close all; clc;
% Let's fix a simple network model.. assume fully connected network and
% with isotropic probability of connection.

N = 10;
A = ones(N) - eye(N);
gossip_max = 2e3;

x0 = 1*rand(N,1); 
x_avg = mean(x0);

% Specify the adaptivity of the agents
tau_x = ones(N,1); 
tau_x([1 2 5 8]) = 10; % agents 1,2 are reluctant with tau = 5
% tau_x = 2*(1 : N);


x_gossip = x0; 

x_model1 = x0; xh_model1 = x0; cnt_xh = ones(N,1);

sq_dist_gos = zeros(gossip_max,1); sq_dist_model1 = sq_dist_gos;
% standard gossip algo...
for gossip_iter = 1 : gossip_max
    % I pick a random node to wake up
    src_node = randint(1,1,[1 N]);
    pos_set = [1:src_node-1 src_node+1:N];
    pos_choice = find(A(src_node,pos_set)>0);
    dst_node_idx = randint(1,1,[1 length(pos_choice)]);
    dst_node = pos_choice(dst_node_idx);
    
    % now run the standard gossip
    tmp_avg = (x_gossip(src_node) + x_gossip(dst_node))/2;
    x_gossip(src_node) = tmp_avg;
    x_gossip(dst_node) = tmp_avg;
    % evaluate the square distance
    sq_dist_gos(gossip_iter) = sum( (x_gossip-x_avg).^2 ) / N;
    
    % now incorporate model 1...
    cnt_xh = cnt_xh + 1;
%     if mod(gossip_iter,5) == 0
        cnt_xh(src_node) = 1; cnt_xh(dst_node) = 1; % reset the counters

        tmp_avg = (x_model1(src_node) + x_model1(dst_node))/2;
        xh_model1(src_node) = tmp_avg; xh_model1(dst_node) = tmp_avg;
%     end
    % now comes the "real" update
    for n = 1 : N
        x_model1(n) = min(1,cnt_xh(n)/tau_x(n))*xh_model1(n) + ...
            max(0, (tau_x(n)-cnt_xh(n))/tau_x(n))*x_model1(n);
    end
    % eval. the squared distance now
    sq_dist_model1(gossip_iter) = sqrt(sum( (x_model1-x_avg).^2 ));
end

sq_dist_gos(end)
 
sq_dist_model1(end)

 sqrt(sum( (x_model1-mean(x_model1)).^2 ))

mean(x_model1)- mean(x_gossip)